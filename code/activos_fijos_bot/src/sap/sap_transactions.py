"""
FASE 3 — TODAVÍA NO IMPLEMENTADA.

Este módulo va a automatizar ÚNICAMENTE la transacción Z_AM_MASIVA
(decisión de negocio: TODO se procesa por esta transacción, sin importar
si la solicitud original era unitaria o masiva). NO se automatizan AS01,
AS02, AS06 ni IE02 por separado (quedan solo como referencia conceptual
en config/asset_type_mapping.py).

Flujo que va a implementar (ver sección 1.4 y 1.5 del documento de
alcance):
    1. Navegar a la transacción Z_AM_MASIVA.
    2. Seleccionar la acción (crear/modificar/borrar) según
       config/asset_type_mapping.py.
    3. Cargar el archivo generado por excel/excel_transformer.py.
    4. Desmarcar el checkbox "Ejecución de test" (SOLO cuando
       settings.SAP_MODO_PRUEBA sea False — ver checklist de traslado en
       GUIA_MODIFICACION.md).
    5. Ejecutar y esperar el log de resultados.
    6. Extraer, por cada fila, si fue éxito o error y el código de activo
       generado (si aplica).

Por qué no se implementa todavía:
    Depende de la Fase 2 (el archivo de carga ya transformado) y de tener
    acceso real a SAP Web para construir sap_xpath_builder.py. Orden de
    desarrollo acordado: Appian -> Excel -> SAP (sección 6 del documento
    de alcance).

# TODO-PENDIENTE-ACCESO-REAL: todo este módulo depende de acceso real a
# SAP Web. Ver TODOs específicos en sap_xpath_builder.py y
# sap_driver_manager.py.
"""

from src.sap.sap_response import build_response


def ejecutar_carga_masiva(archivo_carga_path, accion_carga_masiva, modo_prueba=True):
    """
    Placeholder de la función que va a ejecutar Z_AM_MASIVA.

    Args:
        archivo_carga_path (str): Ruta del archivo ya transformado al
            formato de Z_AM_MASIVA (ver excel/excel_transformer.py).
        accion_carga_masiva (str): Acción a ejecutar dentro de
            Z_AM_MASIVA (ver config/asset_type_mapping.py).
        modo_prueba (bool): Si es True, el checkbox "Ejecución de test"
            debe quedar MARCADO (no se aplican cambios reales en SAP).
            Ver settings.SAP_MODO_PRUEBA y el checklist de traslado en
            GUIA_MODIFICACION.md antes de pasar esto a False alguna vez.

    Returns:
        dict: Respuesta estándar {success, message, data}. En éxito,
            data va a contener el log de resultados (éxitos/errores por
            fila) y los códigos de activo generados.

    Raises:
        NotImplementedError: Siempre, hasta la Fase 3.
    """
    raise NotImplementedError(
        "sap_transactions aún no está implementado (Fase 3). Ver "
        "TODO-PENDIENTE-ACCESO-REAL en este archivo y GUIA_MODIFICACION.md."
    )


# Se deja importado build_response (aunque todavía no se use) para que la
# firma de retorno de ejecutar_carga_masiva, una vez implementada, sea
# consistente con el resto del bot desde el día en que se complete.
__all__ = ["ejecutar_carga_masiva", "build_response"]
