"""
FASE 3 — TODAVÍA NO IMPLEMENTADA.

Va a encargarse de crear el WebDriver y hacer login contra SAP Web,
en paralelo a driver_manager.py + login_page.py de an0016001_appian_flow.

Por qué no se implementa todavía:
    No hay acceso real a SAP Web para confirmar el mecanismo de login
    (usuario/clave vs. SSO) ni si difiere entre los ambientes CP1
    (pruebas) y EP1 (productivo) — ver sección 1.7 (decisiones abiertas)
    del documento de alcance. Se implementa en la Fase 3.

# TODO-PENDIENTE-ACCESO-REAL: confirmar mecanismo de login de SAP Web
# (usuario/clave vs. SSO) y si CP1/EP1 difieren en la URL o en el flujo
# de autenticación.
"""


def crear_driver_sap(browser, timeout, environment):
    """
    Placeholder de la función que va a crear el WebDriver e iniciar
    sesión en SAP Web.

    Args:
        browser (str): Navegador a usar ("edge", igual que appian-flow).
        timeout (int): Tiempo de espera para carga de elementos.
        environment (str): "CP1" o "EP1" (ver settings.SAP_ENVIRONMENT).

    Raises:
        NotImplementedError: Siempre, hasta la Fase 3.
    """
    raise NotImplementedError(
        "sap_driver_manager aún no está implementado (Fase 3). Ver "
        "TODO-PENDIENTE-ACCESO-REAL en este archivo y GUIA_MODIFICACION.md."
    )
