"""
Orquestador principal del bot: encadena las 4 fases del proceso
(Appian -> Excel -> SAP -> Appian) para cada solicitud pendiente.

Estado actual (ver GUIA_MODIFICACION.md para el detalle de fases):
    - FASE 1 (Appian): completamente implementada mediante AppianClient.
    - FASE 2 (Excel) y FASE 3 (SAP): AÚN NO IMPLEMENTADAS. Se dejan
      marcadas con `# TODO-FASE-2` / `# TODO-FASE-3` en vez de
      `TODO-PENDIENTE-ACCESO-REAL`, porque no dependen de que el usuario
      nos dé más información: son el siguiente trabajo de desarrollo, una
      vez la Fase 1 quede validada contra Appian real.
    - FASE 4 (respuesta en Appian): la parte de "avanzar el caso" ya la
      resuelve AppianClient.advance_case(), pero el orquestador todavía no
      arma el `form_data` real porque depende de los resultados de SAP
      (Fase 3), que no existen todavía.

Por qué el orquestador vive separado de AppianClient:
    AppianClient solo sabe hablar con Appian. Este módulo es el que sabe
    de negocio: qué hacer con cada solicitud una vez se tiene su
    información (descubrir -> leer -> transformar -> ejecutar en SAP ->
    responder). Mantenerlos separados permite probar cada pieza de forma
    aislada (ver tests/test_appian_client.py) sin necesitar todo el flujo
    completo.
"""

from src.appian.appian_client import AppianClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


def procesar_solicitud(appian_client, case_id):
    """
    Procesa una única solicitud de principio a fin.

    Por ahora solo cubre la Fase 1 (leer la solicitud y descargar el
    Excel adjunto). El resultado se loguea para poder validar, con casos
    reales, que el bot identifica correctamente el tipo de activo, la
    acción y descarga el archivo correcto (criterio de cierre de la Fase
    1 acordado con el usuario).

    Args:
        appian_client (AppianClient): Cliente ya iniciado (start() llamado).
        case_id (str): Número de la solicitud a procesar.

    Returns:
        dict: Respuesta estándar. En éxito, data incluye tipo_activo,
            accion y la lista de archivos descargados.
    """
    logger.info("Procesando solicitud %s", case_id)

    case_response = appian_client.get_case_data(case_id, download_attachments=True)
    if not case_response["success"]:
        logger.error("No fue posible leer la solicitud %s: %s", case_id, case_response["message"])
        return case_response

    info_df = case_response["data"]["info"]
    files = case_response["data"]["files"]

    parse_response = appian_client.parse_asset_request(info_df)
    if not parse_response["success"]:
        logger.error(
            "No fue posible interpretar la solicitud %s: %s", case_id, parse_response["message"]
        )
        return parse_response

    tipo_activo = parse_response["data"]["tipo_activo"]
    accion = parse_response["data"]["accion"]

    logger.info(
        "Solicitud %s identificada como tipo_activo=%s, accion=%s, %d archivo(s) descargado(s).",
        case_id,
        tipo_activo,
        accion,
        len(files),
    )

    # TODO-FASE-2: aquí va la llamada a excel_reader/excel_transformer para
    # convertir `files` al formato de carga de Z_AM_MASIVA, una vez se
    # conozca el formato exacto (ver excel/excel_transformer.py).
    #
    # TODO-FASE-3: aquí va la llamada a sap_transactions para ejecutar
    # Z_AM_MASIVA con el archivo transformado y capturar el log de resultado.
    #
    # TODO-FASE-4: aquí va excel_writer + appian_client.advance_case() para
    # responder la solicitud con los códigos SAP generados.

    return {
        "success": True,
        "message": "Fase 1 completada (lectura de Appian). Fases 2-4 pendientes de desarrollo.",
        "data": {
            "case_id": case_id,
            "tipo_activo": tipo_activo,
            "accion": accion,
            "files": files,
        },
    }


def ejecutar_ciclo(appian_client):
    """
    Ejecuta una pasada completa: descubre las solicitudes pendientes y
    procesa cada una.

    Args:
        appian_client (AppianClient): Cliente ya iniciado.

    Returns:
        list[dict]: Un resultado (ver procesar_solicitud) por cada
            solicitud encontrada.
    """
    discover_response = appian_client.discover_pending_cases()
    if not discover_response["success"]:
        logger.error("No fue posible descubrir solicitudes pendientes: %s", discover_response["message"])
        return []

    case_ids = discover_response["data"]
    if not case_ids:
        logger.info("No hay solicitudes pendientes en este ciclo.")
        return []

    resultados = []
    for case_id in case_ids:
        try:
            resultados.append(procesar_solicitud(appian_client, case_id))
        except Exception:  # noqa: BLE001 - una solicitud con error no debe tumbar el ciclo completo
            logger.exception("Error inesperado procesando la solicitud %s", case_id)

    return resultados


def main():
    """
    Punto de entrada del bot: inicia sesión en Appian y ejecuta un único
    ciclo de descubrimiento + procesamiento.

    Nota: la ejecución periódica (revisar la bandeja cada N segundos, ver
    settings.POLL_INTERVAL_SECONDS) se deja a criterio de cómo se vaya a
    programar el bot en el PC de la empresa (p. ej. Task Scheduler de
    Windows corriendo este script cada N minutos, en vez de un loop
    infinito con time.sleep() dentro del propio proceso). Ver
    GUIA_MODIFICACION.md, checklist de traslado.
    """
    appian_client = AppianClient()

    start_response = appian_client.start()
    if not start_response["success"]:
        logger.error("No fue posible iniciar el bot: %s", start_response["message"])
        return

    try:
        ejecutar_ciclo(appian_client)
    finally:
        appian_client.close()


if __name__ == "__main__":
    main()
