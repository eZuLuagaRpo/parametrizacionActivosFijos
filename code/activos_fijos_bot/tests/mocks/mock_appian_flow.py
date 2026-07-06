"""
Mock de AppianFlow para poder probar AppianClient sin Appian real.

Por qué existe:
    En este PC de desarrollo no hay acceso a Appian ni está instalada la
    librería real an0016001_appian_flow (solo se copió su código fuente
    como referencia, ver README del proyecto). Para poder escribir y
    correr pruebas unitarias de todas formas, se reemplaza la clase
    AppianFlow por este doble de prueba con el mismo contrato de
    respuestas {success, message, data}.

Cómo se usa:
    Se inyecta con unittest.mock.patch sobre
    "src.appian.appian_client.AppianFlow", configurando de antemano qué
    debe responder cada método. Ver tests/test_appian_client.py.
"""

from selenium.common.exceptions import TimeoutException


def build_response(success, message, data=None):
    """Réplica del contrato de respuesta de an0016001_appian_flow.response."""
    return {"success": success, "message": message, "data": data}


class FakeElement:
    """Elemento HTML falso: solo lo mínimo que appian_client.py usa."""

    def __init__(self, text=""):
        self.text = text

    def click(self):
        pass


class FakeSeleniumDriver:
    """
    Driver de Selenium falso usado por discover_pending_cases().

    En vez de reimplementar un motor de XPath, este doble reconoce
    exactamente los mismos locators que produce XPathBuilder para los
    casos que appian_client.py necesita:
        - //*[@data-text='Seguimiento de Solicitudes']  -> menú
        - //a[contains(@href,'/tempo/cases/')]          -> filas de la grilla
        - //*[@data-empty-grid-message='true']          -> grilla vacía

    Se configura con listas de "elementos" ya armadas, simulando lo que
    se vería en pantalla en cada escenario de prueba.
    """

    def __init__(self, case_links=None, grid_vacia=False):
        self._menu_element = [FakeElement("Seguimiento de Solicitudes")]
        self._case_links = [FakeElement(text) for text in (case_links or [])]
        self._grid_vacia = grid_vacia
        self.executed_scripts = []

    def find_elements(self, by, value):
        if "data-text='Seguimiento de Solicitudes'" in value:
            return self._menu_element
        if "data-empty-grid-message" in value:
            return [FakeElement()] if self._grid_vacia else []
        if "/tempo/cases/" in value:
            return [] if self._grid_vacia else self._case_links
        return []

    def execute_script(self, script, *args):
        self.executed_scripts.append((script, args))


class FakeWait:
    """
    Doble de WebDriverWait: ejecuta la condición inmediatamente contra el
    FakeSeleniumDriver, sin reintentos ni tiempos de espera reales.

    Si la condición retorna un valor "falsy" (lista vacía, False, etc.),
    se simula un timeout real levantando TimeoutException, tal como lo
    haría Selenium si nunca se cumple la condición.
    """

    def __init__(self, driver):
        self.driver = driver

    def until(self, condition):
        result = condition(self.driver)
        if not result:
            raise TimeoutException("Condición no cumplida (FakeWait)")
        return result


class MockAppianFlow:
    """
    Doble de prueba de la clase AppianFlow completa.

    Cada método puede configurarse por fuera (antes de llamarlo) asignando
    directamente a las respuestas por defecto, o se puede crear una
    subclase para escenarios más específicos.
    """

    def __init__(self, url, download_dir=None, browser="edge", timeout=90, timeout_files=600):
        self.url = url
        self.download_dir = download_dir or "C:/fake/downloads"
        self.browser = browser
        self.timeout = timeout
        self.timeout_files = timeout_files

        # Selenium falso reutilizado por discover_pending_cases()
        self.driver = FakeSeleniumDriver()
        self.wait = FakeWait(self.driver)

        # Respuestas configurables por la prueba antes de invocar el método.
        self.start_response = build_response(True, "Aplicación iniciada correctamente")
        self.search_case_response = build_response(True, "OK")
        self.get_case_data_response = build_response(True, "OK", {"info": None, "files": []})
        self.advance_case_response = build_response(True, "OK")
        self.cerrar_called = False

        # Registro de llamadas, útil para verificar (aserciones) en las pruebas.
        self.calls = []

    def start(self, user=None, password=None):
        self.calls.append(("start", user, password))
        return self.start_response

    def search_case(self, case_id):
        self.calls.append(("search_case", case_id))
        return self.search_case_response

    def get_case_data(self, case_id, download_attachments=False):
        self.calls.append(("get_case_data", case_id, download_attachments))
        return self.get_case_data_response

    def advance_case(self, case_id, form_data):
        self.calls.append(("advance_case", case_id, form_data))
        return self.advance_case_response

    def cerrar(self):
        self.calls.append(("cerrar",))
        self.cerrar_called = True
