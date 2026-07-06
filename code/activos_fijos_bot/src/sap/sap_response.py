"""
Objeto de respuesta estándar para el módulo sap/, con el mismo contrato
que an0016001_appian_flow.response.build_response: {success, message, data}.

Este archivo SÍ se puede implementar desde ya (no depende de acceso real
a SAP): es solo una convención de datos, igual que la de appian-flow, para
que todo el bot (Appian, Excel, SAP) hable el mismo "idioma" de respuestas.
"""


def build_response(success, message, data=None):
    """
    Crea una respuesta estándar para las operaciones del módulo SAP.

    Se mantiene como función independiente (en vez de reutilizar
    an0016001_appian_flow.response.build_response) para que sap/ no
    dependa de appian-flow: son capas distintas del bot y no deberían
    acoplarse entre sí, aunque hoy el contrato sea idéntico.

    Args:
        success (bool): Indica si la operación fue exitosa.
        message (str): Mensaje descriptivo del resultado.
        data (any, opcional): Información adicional.

    Returns:
        dict: {"success": bool, "message": str, "data": any}
    """
    return {"success": success, "message": message, "data": data}
