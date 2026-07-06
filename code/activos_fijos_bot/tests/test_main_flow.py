"""
Pruebas unitarias del orquestador (Fase 1: descubrir + leer solicitudes).

Estas pruebas NO usan AppianClient real ni MockAppianFlow: usan un doble
todavía más simple (FakeAppianClientParaOrquestador) que solo respeta el
contrato público de AppianClient (get_case_data, parse_asset_request,
discover_pending_cases). Esto mantiene las pruebas del orquestador
enfocadas en SU lógica (qué hace con cada solicitud descubierta), sin
depender de los detalles de Selenium que ya se prueban en
test_appian_client.py.
"""

import pandas as pd

from src.config.asset_type_mapping import AccionSolicitud, TipoActivo
from src.orchestrator.main_flow import ejecutar_ciclo, procesar_solicitud


def _respuesta(success, message="OK", data=None):
    return {"success": success, "message": message, "data": data}


class FakeAppianClientParaOrquestador:
    """Doble mínimo de AppianClient para probar el orquestador."""

    def __init__(self):
        self.discover_response = _respuesta(True, data=[])
        self.get_case_data_responses = {}
        self.parse_asset_request_responses = {}
        self.advance_case_calls = []

    def discover_pending_cases(self):
        return self.discover_response

    def get_case_data(self, case_id, download_attachments=True):
        return self.get_case_data_responses[case_id]

    def parse_asset_request(self, info_df):
        # Se identifica la respuesta configurada por el contenido del
        # propio DataFrame (marcador "case_id" en la primera fila), para
        # no depender de instancias == entre DataFrames.
        case_id = info_df.attrs.get("case_id")
        return self.parse_asset_request_responses[case_id]

    def advance_case(self, case_id, form_data):
        self.advance_case_calls.append((case_id, form_data))
        return _respuesta(True)


def _info_df(case_id):
    df = pd.DataFrame([{"label": "Tipo de Activo", "value": "BRP"}])
    df.attrs["case_id"] = case_id
    return df


def test_procesar_solicitud_exitoso_retorna_tipo_accion_y_archivos():
    client = FakeAppianClientParaOrquestador()
    info_df = _info_df("ABCD-1111")
    files = [{"file": "solicitud.xlsx", "path": "C:/fake", "full_path": "C:/fake/solicitud.xlsx"}]

    client.get_case_data_responses["ABCD-1111"] = _respuesta(
        True, data={"info": info_df, "files": files}
    )
    client.parse_asset_request_responses["ABCD-1111"] = _respuesta(
        True, data={"tipo_activo": TipoActivo.BRP, "accion": AccionSolicitud.CREACION}
    )

    resultado = procesar_solicitud(client, "ABCD-1111")

    assert resultado["success"] is True
    assert resultado["data"]["tipo_activo"] == TipoActivo.BRP
    assert resultado["data"]["accion"] == AccionSolicitud.CREACION
    assert resultado["data"]["files"] == files


def test_procesar_solicitud_falla_si_no_se_puede_leer_el_caso():
    client = FakeAppianClientParaOrquestador()
    client.get_case_data_responses["ABCD-2222"] = _respuesta(False, message="Timeout buscando el caso")

    resultado = procesar_solicitud(client, "ABCD-2222")

    assert resultado["success"] is False
    assert "Timeout" in resultado["message"]


def test_procesar_solicitud_falla_si_no_se_puede_interpretar_la_solicitud():
    client = FakeAppianClientParaOrquestador()
    info_df = _info_df("ABCD-3333")
    client.get_case_data_responses["ABCD-3333"] = _respuesta(
        True, data={"info": info_df, "files": []}
    )
    client.parse_asset_request_responses["ABCD-3333"] = _respuesta(
        False, message="Valor de tipo de activo no reconocido"
    )

    resultado = procesar_solicitud(client, "ABCD-3333")

    assert resultado["success"] is False
    assert "no reconocido" in resultado["message"]


def test_ejecutar_ciclo_sin_solicitudes_pendientes():
    client = FakeAppianClientParaOrquestador()
    client.discover_response = _respuesta(True, data=[])

    resultados = ejecutar_ciclo(client)

    assert resultados == []


def test_ejecutar_ciclo_procesa_todas_las_solicitudes_descubiertas():
    client = FakeAppianClientParaOrquestador()
    client.discover_response = _respuesta(True, data=["ABCD-1111", "ABCD-2222"])

    for case_id in ["ABCD-1111", "ABCD-2222"]:
        info_df = _info_df(case_id)
        client.get_case_data_responses[case_id] = _respuesta(True, data={"info": info_df, "files": []})
        client.parse_asset_request_responses[case_id] = _respuesta(
            True, data={"tipo_activo": TipoActivo.BRP, "accion": AccionSolicitud.CREACION}
        )

    resultados = ejecutar_ciclo(client)

    assert len(resultados) == 2
    assert all(r["success"] for r in resultados)


def test_ejecutar_ciclo_continua_si_una_solicitud_falla():
    client = FakeAppianClientParaOrquestador()
    client.discover_response = _respuesta(True, data=["ABCD-OK", "ABCD-FALLA"])

    info_ok = _info_df("ABCD-OK")
    client.get_case_data_responses["ABCD-OK"] = _respuesta(True, data={"info": info_ok, "files": []})
    client.parse_asset_request_responses["ABCD-OK"] = _respuesta(
        True, data={"tipo_activo": TipoActivo.BRP, "accion": AccionSolicitud.CREACION}
    )

    # "ABCD-FALLA" ni siquiera está registrado en get_case_data_responses,
    # lo que provoca un KeyError dentro de procesar_solicitud: simula un
    # error inesperado y verifica que el ciclo sigue con las demás solicitudes.
    resultados = ejecutar_ciclo(client)

    assert len(resultados) == 1
    assert resultados[0]["success"] is True


def test_ejecutar_ciclo_retorna_vacio_si_discover_falla():
    client = FakeAppianClientParaOrquestador()
    client.discover_response = _respuesta(False, message="Timeout esperando la grilla")

    resultados = ejecutar_ciclo(client)

    assert resultados == []
