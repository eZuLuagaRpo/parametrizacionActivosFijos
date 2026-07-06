"""
FASE 2 — TODAVÍA NO IMPLEMENTADA.

Este es el módulo que reemplaza por completo la macro de Excel actual.
Va a traducir el Excel que el usuario adjuntó en Appian (leído por
excel_reader.py) al formato EXACTO que exige la transacción Z_AM_MASIVA
en SAP, sin pasar por ninguna macro ni archivo intermedio.

Por qué no se implementa todavía:
    1. Orden de desarrollo: falta cerrar y validar la Fase 1 (Appian)
       contra un caso real antes de empezar esta fase (sección 6 del
       documento de alcance).
    2. Formato pendiente: el usuario todavía no ha compartido las
       columnas, hoja(s) y tipos de dato exactos que espera el archivo de
       carga de Z_AM_MASIVA. Sin eso, cualquier implementación sería
       adivinar la estructura de la macro que estamos reemplazando.

# TODO-PENDIENTE-FORMATO-Z_AM_MASIVA: este módulo completo depende de que
# el usuario comparta el formato exacto de carga de Z_AM_MASIVA (columnas,
# nombre(s) de hoja, tipos de dato esperados, y si el formato cambia según
# la acción -crear/modificar/borrar- o el tipo de activo). Ver
# config/asset_type_mapping.py para dónde queda registrada esa
# configuración por tipo de activo, y GUIA_MODIFICACION.md para el paso a
# paso de cómo completar este módulo cuando llegue esa información.
"""


def transformar_a_formato_z_am_masiva(excel_usuario_path, tipo_activo, accion):
    """
    Placeholder de la función que va a reemplazar la macro de Excel.

    Args:
        excel_usuario_path (str): Ruta del Excel descargado del caso de Appian.
        tipo_activo (TipoActivo): Tipo de activo identificado en Appian.
        accion (AccionSolicitud): Acción solicitada (crear/modificar/borrar).

    Returns:
        dict: Respuesta estándar {success, message, data}. En éxito, data
            será la ruta del archivo ya en formato Z_AM_MASIVA, listo para
            cargarse en sap/sap_transactions.py.

    Raises:
        NotImplementedError: Siempre, hasta que se conozca el formato
            exacto de Z_AM_MASIVA. Ver TODO-PENDIENTE-FORMATO-Z_AM_MASIVA
            en el encabezado de este archivo.
    """
    raise NotImplementedError(
        "excel_transformer aún no está implementado: falta el formato de "
        "carga de Z_AM_MASIVA (columnas, hoja, tipos de dato). Ver "
        "TODO-PENDIENTE-FORMATO-Z_AM_MASIVA en este archivo y "
        "GUIA_MODIFICACION.md."
    )
