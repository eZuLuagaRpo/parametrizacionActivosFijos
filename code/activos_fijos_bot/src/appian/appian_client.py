"""
Wrapper delgado sobre la librería interna `an0016001_appian_flow`.

Qué SÍ hace este módulo:
    - Orquestar el ciclo de vida de AppianFlow (start/cerrar) con manejo
      de errores y logging estandarizados para el resto del bot.
    - Encadenar pasos que la librería exige por separado (p. ej.
      `get_case_data` y `advance_case` requieren haber llamado antes
      `search_case`) en un único método más simple de usar desde el
      orquestador.
    - Agregar la ÚNICA pieza que appian-flow no expone todavía:
      descubrir qué solicitudes están pendientes en la bandeja SIN
      conocer de antemano el número de caso (appian-flow solo permite
      buscar por case_id exacto con `search_case`).
    - Traducir la información cruda de un caso (DataFrame label/value)
      a los conceptos de negocio del bot (tipo de activo, acción).

Qué NO hace este módulo (a propósito):
    - No reimplementa login, manejo de formularios dinámicos, ni
      descarga de adjuntos: eso ya lo resuelve appian-flow y aquí solo
      se consume.
    - No decide a qué transacción de SAP va cada solicitud (eso vive en
      config/asset_type_mapping.py) ni transforma el Excel (Fase 2).

Decisión de arquitectura (confirmada con el usuario): NO forkeamos ni
copiamos el código fuente de appian-flow. Todo lo nuevo que necesitamos
(discover_pending_cases) se construye reutilizando piezas PÚBLICAS de la
librería (`self.driver`, `self.wait`, `XPathBuilder`), para poder seguir
actualizando la librería con `pip install --upgrade` sin conflictos.
"""

import re

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

# Import protegido: en ESTE PC de desarrollo la librería
# an0016001_appian_flow no está instalada (solo existe como copia de
# referencia extraída del site-packages de la empresa, ver README.md).
# En el PC de la empresa sí estará instalada vía `pip install
# an0016001_appian_flow` y este bloque importa las clases reales sin
# ningún cambio de comportamiento.
#
# El fallback de abajo NO reimplementa lógica de negocio ni automatización
# (login, formularios, descargas siguen sin poder probarse sin la
# librería real): solo repone dos utilidades triviales de una línea
# (build_response y XPathBuilder.by_data_text) para que este módulo se
# pueda importar y probar con MockAppianFlow (ver tests/mocks/) sin
# depender de que el paquete real esté físicamente disponible aquí.
try:
    from an0016001_appian_flow.appian_flow import AppianFlow
    from an0016001_appian_flow.response import build_response
    from an0016001_appian_flow.xpath_builder import XPathBuilder
except ImportError:  # pragma: no cover - solo ocurre en este PC de desarrollo

    AppianFlow = None

    def build_response(success, message, data=None):
        return {"success": success, "message": message, "data": data}

    class XPathBuilder:  # noqa: N801 - mismo nombre que la clase real, a propósito
        @staticmethod
        def by_data_text(text):
            return (By.XPATH, f"//*[@data-text='{text}']")

from src.config import settings
from src.config.asset_type_mapping import AccionSolicitud, TipoActivo
from src.utils.logger import get_logger

logger = get_logger(__name__)

# -------------------------------------------------
# Configuración de interpretación de campos de Appian
# -------------------------------------------------
# TODO-PENDIENTE-ACCESO-REAL: estos son los nombres de label EXACTOS
# (case-sensitive) que get_case_data() debe encontrar en el detalle del
# caso de Appian para poder identificar el tipo de activo y la acción
# solicitada. Hay que confirmarlos abriendo un caso real y comparando
# contra la columna "label" del DataFrame que retorna get_case_data.
CAMPO_TIPO_ACTIVO = "Tipo de Activo"
CAMPO_ACCION_SOLICITADA = "Acción Solicitada"

# TODO-PENDIENTE-ACCESO-REAL: mapeo entre el texto EXACTO que el usuario ve
# y selecciona en el formulario de Appian (columna "value") y nuestros
# Enums internos. Ajustar cuando se conozcan los textos reales de las
# listas desplegables en Appian.
VALOR_APPIAN_A_TIPO_ACTIVO = {
    "MASCARA": TipoActivo.MASCARA,
    "BRP": TipoActivo.BRP,
    "PRJ": TipoActivo.PRJ,
    "DIFERIDOS Y RENOVACIONES": TipoActivo.DIFERIDOS_RENOVACIONES,
    "MEJORAS": TipoActivo.MEJORAS,
}

VALOR_APPIAN_A_ACCION = {
    "CREACION": AccionSolicitud.CREACION,
    "CREACIÓN": AccionSolicitud.CREACION,
    "MODIFICACION": AccionSolicitud.MODIFICACION,
    "MODIFICACIÓN": AccionSolicitud.MODIFICACION,
    "ELIMINACION": AccionSolicitud.ELIMINACION,
    "ELIMINACIÓN": AccionSolicitud.ELIMINACION,
}

# TODO-PENDIENTE-ACCESO-REAL: patrón para reconocer, dentro de la grilla de
# "Seguimiento de Solicitudes", qué texto corresponde a un número de caso.
# Se basó en el único ejemplo visible en appian-flow: create_case() extrae
# el número generado con el patrón //p//strong[contains(text(),'-')], lo
# que sugiere un formato tipo "XXXX-1234". Validar con un caso real y
# ajustar el regex si el formato es distinto.
PATRON_NUMERO_CASO = re.compile(r"^[A-Za-z0-9]+-[A-Za-z0-9]+$")


class AppianClient:
    """
    Punto de entrada único del bot hacia Appian.

    El orquestador (orchestrator/main_flow.py) solo debería hablar con
    esta clase, nunca importar AppianFlow directamente. Así, si el día de
    mañana cambia la forma de descubrir solicitudes pendientes (p. ej. se
    reemplaza el scraping de la grilla por download_report), el cambio
    queda contenido aquí.
    """

    def __init__(
        self,
        url=None,
        download_dir=None,
        browser=None,
        timeout=None,
        timeout_files=None,
    ):
        self.url = url or settings.APPIAN_URL
        self.download_dir = download_dir or settings.DOWNLOAD_DIR
        self.browser = browser or settings.APPIAN_BROWSER
        self.timeout = timeout or settings.APPIAN_TIMEOUT
        self.timeout_files = timeout_files or settings.APPIAN_TIMEOUT_FILES

        # El objeto AppianFlow se crea en start(), no aquí, para no abrir
        # un navegador real solo por instanciar AppianClient (por ejemplo,
        # al construir el objeto dentro de una prueba unitaria).
        self._flow = None

    # -------------------------------------------------
    # CICLO DE VIDA
    # -------------------------------------------------
    def start(self):
        """
        Abre el navegador e inicia sesión en Appian.

        Returns:
            dict: Respuesta estándar {success, message, data}.
        """
        if AppianFlow is None:
            return build_response(
                False,
                "La librería an0016001_appian_flow no está disponible en este "
                "entorno. Si esto ocurre en el PC de la empresa, instalarla con: "
                "pip install an0016001_appian_flow.",
            )

        logger.info("Iniciando AppianFlow contra %s", self.url)

        self._flow = AppianFlow(
            url=self.url,
            download_dir=self.download_dir,
            browser=self.browser,
            timeout=self.timeout,
            timeout_files=self.timeout_files,
        )

        response = self._flow.start(user=settings.APPIAN_USER, password=settings.APPIAN_PASSWORD)

        if not response["success"]:
            logger.error("No fue posible iniciar sesión en Appian: %s", response["message"])
        else:
            logger.info("Sesión de Appian iniciada correctamente.")

        return response

    def close(self):
        """Cierra el navegador. Debe llamarse siempre, incluso si hubo error."""
        if self._flow is not None:
            self._flow.cerrar()
            self._flow = None
            logger.info("Navegador de Appian cerrado.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    # -------------------------------------------------
    # DESCUBRIMIENTO DE SOLICITUDES PENDIENTES
    # (lo único que appian-flow no resuelve todavía)
    # -------------------------------------------------
    def discover_pending_cases(self):
        """
        Identifica en pantalla qué números de caso están pendientes en la
        bandeja de "Seguimiento de Solicitudes", sin necesidad de conocerlos
        de antemano.

        TODO-PENDIENTE-ACCESO-REAL: esta implementación es un punto de
        partida razonable basado en los patrones que sí existen en
        appian-flow (mismo menú, mismo indicador de grilla vacía
        data-empty-grid-message, mismo formato de número de caso con
        guión). Falta validar con un caso real:
            1. Si al entrar a "Seguimiento de Solicitudes" sin buscar nada
               ya aparece una grilla con las solicitudes pendientes
               asignadas al usuario, o si hace falta aplicar algún filtro
               (p. ej. "Estado = Pendiente") antes.
            2. Si hay paginación (¿se debe recorrer más de una página?).
            3. Si el regex PATRON_NUMERO_CASO reconoce correctamente el
               formato real del número de caso.
            Ajustar esta función y sus constantes en cuanto se tenga
            acceso a Appian real, siguiendo la guía en GUIA_MODIFICACION.md.

        Returns:
            dict: Respuesta estándar. En caso de éxito, `data` es una
                lista de strings con los case_id pendientes (puede ser
                una lista vacía si no hay solicitudes).
        """
        if self._flow is None:
            return build_response(False, "Debe llamarse start() antes de discover_pending_cases().")

        driver = self._flow.driver
        wait = self._flow.wait

        step = "Abriendo menú Seguimiento de Solicitudes"
        try:
            # Se usa el mismo patrón "wait.until(lambda d: d.find_elements(...))"
            # que ya usa cases_page.py de appian-flow (en vez de
            # EC.presence_of_element_located), porque solo depende de
            # find_elements() y así es más simple de probar con mocks.
            menu_locator = XPathBuilder.by_data_text("Seguimiento de Solicitudes")
            menu_elements = wait.until(lambda d: d.find_elements(*menu_locator))
            driver.execute_script("arguments[0].click();", menu_elements[0])

            step = "Esperando que cargue la grilla de solicitudes"
            wait.until(
                lambda d: (
                    d.find_elements(By.XPATH, "//a[contains(@href,'/tempo/cases/')]")
                    or d.find_elements(By.XPATH, "//*[@data-empty-grid-message='true']")
                )
            )

            step = "Verificando si la grilla está vacía"
            if driver.find_elements(By.XPATH, "//*[@data-empty-grid-message='true']"):
                logger.info("No se encontraron solicitudes pendientes en la bandeja.")
                return build_response(True, "No hay solicitudes pendientes.", [])

            step = "Extrayendo números de caso de la grilla"
            links = driver.find_elements(By.XPATH, "//a[contains(@href,'/tempo/cases/')]")

            pending_cases = []
            for link in links:
                text = link.text.strip()
                if text and PATRON_NUMERO_CASO.match(text) and text not in pending_cases:
                    pending_cases.append(text)

            logger.info("Se encontraron %d solicitud(es) pendiente(s): %s", len(pending_cases), pending_cases)
            return build_response(
                True,
                f"Se encontraron {len(pending_cases)} solicitud(es) pendiente(s).",
                pending_cases,
            )

        except TimeoutException:
            return build_response(False, f"Timeout en el paso: {step}")
        except Exception as e:  # noqa: BLE001 - se estandariza la respuesta de error
            return build_response(False, f"Error al descubrir solicitudes pendientes ({step}). {e}")

    # -------------------------------------------------
    # CONSULTA Y AVANCE DE CASOS
    # (encadenan search_case, que appian-flow exige por separado)
    # -------------------------------------------------
    def get_case_data(self, case_id, download_attachments=True):
        """
        Busca un caso y retorna su información y adjuntos descargados.

        Encadena `search_case` + `get_case_data` de appian-flow, ya que la
        librería exige que el primero se haya ejecutado antes del segundo.

        Args:
            case_id (str): Número de caso.
            download_attachments (bool): Si se deben descargar los Excels
                adjuntos por el usuario. En el flujo real del bot siempre
                debería ser True; se deja el parámetro para pruebas.

        Returns:
            dict: Respuesta estándar. En éxito, data = {"info": DataFrame,
                "files": list[dict]} tal como lo retorna appian-flow.
        """
        if self._flow is None:
            return build_response(False, "Debe llamarse start() antes de get_case_data().")

        search_response = self._flow.search_case(case_id)
        if not search_response["success"]:
            logger.warning("No se pudo abrir el caso %s: %s", case_id, search_response["message"])
            return search_response

        return self._flow.get_case_data(case_id, download_attachments=download_attachments)

    def advance_case(self, case_id, form_data):
        """
        Busca un caso y lo avanza con la información entregada.

        Al igual que get_case_data, encadena `search_case` + `advance_case`
        porque appian-flow exige haber abierto el caso primero.

        Args:
            case_id (str): Número de caso.
            form_data (dict): Ver documentación de AppianFlow.advance_case.

        Returns:
            dict: Respuesta estándar.
        """
        if self._flow is None:
            return build_response(False, "Debe llamarse start() antes de advance_case().")

        search_response = self._flow.search_case(case_id)
        if not search_response["success"]:
            logger.warning("No se pudo abrir el caso %s: %s", case_id, search_response["message"])
            return search_response

        return self._flow.advance_case(case_id, form_data)

    # -------------------------------------------------
    # INTERPRETACIÓN DE NEGOCIO
    # -------------------------------------------------
    def parse_asset_request(self, case_info_df):
        """
        Traduce el DataFrame label/value de un caso a los conceptos de
        negocio que el resto del bot necesita: tipo de activo y acción.

        Args:
            case_info_df (pandas.DataFrame): El `data["info"]` que retorna
                get_case_data.

        Returns:
            dict: Respuesta estándar. En éxito, data = {
                "tipo_activo": TipoActivo, "accion": AccionSolicitud
            }.
        """
        try:
            tipo_raw = self._buscar_valor_por_label(case_info_df, CAMPO_TIPO_ACTIVO)
            accion_raw = self._buscar_valor_por_label(case_info_df, CAMPO_ACCION_SOLICITADA)

            if tipo_raw is None or accion_raw is None:
                return build_response(
                    False,
                    "No se encontraron los campos "
                    f"'{CAMPO_TIPO_ACTIVO}' y/o '{CAMPO_ACCION_SOLICITADA}' en el caso. "
                    "Revisar el nombre exacto del label en Appian (ver "
                    "TODO-PENDIENTE-ACCESO-REAL en appian_client.py).",
                )

            tipo_activo = VALOR_APPIAN_A_TIPO_ACTIVO.get(tipo_raw.strip().upper())
            accion = VALOR_APPIAN_A_ACCION.get(accion_raw.strip().upper())

            if tipo_activo is None:
                return build_response(
                    False,
                    f"Valor de tipo de activo no reconocido: '{tipo_raw}'. "
                    "Agréguelo a VALOR_APPIAN_A_TIPO_ACTIVO en appian_client.py.",
                )

            if accion is None:
                return build_response(
                    False,
                    f"Valor de acción no reconocido: '{accion_raw}'. "
                    "Agréguelo a VALOR_APPIAN_A_ACCION en appian_client.py.",
                )

            return build_response(
                True,
                "OK",
                {"tipo_activo": tipo_activo, "accion": accion},
            )

        except Exception as e:  # noqa: BLE001
            return build_response(False, f"Error interpretando la solicitud: {e}")

    @staticmethod
    def _buscar_valor_por_label(case_info_df, label):
        """
        Busca en el DataFrame label/value el valor de un campo por su label.

        Returns:
            str | None: El valor encontrado, o None si el label no existe.
        """
        match = case_info_df.loc[case_info_df["label"] == label, "value"]
        if match.empty:
            return None
        return match.iloc[0]
