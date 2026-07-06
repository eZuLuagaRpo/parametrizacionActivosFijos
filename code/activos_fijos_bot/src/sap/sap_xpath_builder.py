"""
FASE 3 — TODAVÍA NO IMPLEMENTADA.

Aquí van a vivir TODOS los XPaths/selectores de SAP Web, centralizados,
siguiendo el mismo patrón que XPathBuilder en an0016001_appian_flow.

Por qué se centralizan aquí y no sueltos en sap_transactions.py:
    Cuando el usuario tenga acceso real a SAP Web y necesite ajustar un
    selector (porque cambió el HTML, o porque el que se dejó de
    referencia estaba mal), debe poder ir a UN solo archivo, no rastrear
    XPaths dispersos en medio de la lógica de negocio. Ver
    GUIA_MODIFICACION.md, sección "Dónde ubicar cada XPath nuevo".

Por qué no se implementa todavía:
    No hay acceso real a SAP Web para inspeccionar el HTML real de la
    transacción Z_AM_MASIVA. Cualquier XPath escrito ahora sería una
    adivinanza. Se implementa en la Fase 3, después de que Appian (Fase 1)
    y Excel (Fase 2) estén validados (sección 6 del documento de alcance).

# TODO-PENDIENTE-ACCESO-REAL: todos los XPaths de esta clase (login SAP,
# navegación a Z_AM_MASIVA, campo de carga de archivo, checkbox "Ejecución
# de test", botón ejecutar, y la grilla/log de resultados) quedan
# pendientes de definir con acceso real a SAP Web (ambientes CP1/EP1).
"""


class SapXPathBuilder:
    """
    Selectores de SAP Web, centralizados igual que XPathBuilder de
    appian-flow. Se deja la clase creada (vacía de selectores reales)
    para que sap_transactions.py ya pueda importarla desde ya, y que
    completar los XPaths reales sea solo cuestión de llenar estos
    métodos, sin tener que tocar la lógica de negocio.
    """

    @staticmethod
    def login_usuario():
        # TODO-PENDIENTE-ACCESO-REAL: selector del campo de usuario en el
        # login web de SAP (confirmar si es igual en CP1 y EP1).
        raise NotImplementedError("Pendiente: XPath de login de SAP no definido todavía.")

    @staticmethod
    def login_password():
        # TODO-PENDIENTE-ACCESO-REAL: selector del campo de contraseña.
        raise NotImplementedError("Pendiente: XPath de login de SAP no definido todavía.")

    @staticmethod
    def campo_transaccion():
        # TODO-PENDIENTE-ACCESO-REAL: selector del campo donde se escribe
        # el código de transacción (Z_AM_MASIVA) en la barra de comandos de SAP.
        raise NotImplementedError("Pendiente: XPath de barra de transacción no definido todavía.")

    @staticmethod
    def campo_carga_archivo():
        # TODO-PENDIENTE-ACCESO-REAL: selector del input de tipo "file" (o
        # botón que lo abre) para cargar el Excel en Z_AM_MASIVA.
        raise NotImplementedError("Pendiente: XPath de carga de archivo no definido todavía.")

    @staticmethod
    def checkbox_ejecucion_test():
        # TODO-PENDIENTE-ACCESO-REAL: selector del checkbox "Ejecución de
        # test". IMPORTANTE (ver GUIA_MODIFICACION.md checklist): debe
        # quedar MARCADO por defecto en toda prueba, y solo desmarcarse
        # cuando el usuario confirme explícitamente que se puede ejecutar
        # en modo real.
        raise NotImplementedError("Pendiente: XPath de checkbox de test no definido todavía.")

    @staticmethod
    def boton_ejecutar():
        # TODO-PENDIENTE-ACCESO-REAL: selector del botón que ejecuta la
        # carga masiva dentro de Z_AM_MASIVA.
        raise NotImplementedError("Pendiente: XPath de botón ejecutar no definido todavía.")

    @staticmethod
    def grilla_resultado_log():
        # TODO-PENDIENTE-ACCESO-REAL: selector de la grilla/log de
        # resultados que SAP genera por cada registro procesado (éxito/error).
        raise NotImplementedError("Pendiente: XPath de log de resultados no definido todavía.")
