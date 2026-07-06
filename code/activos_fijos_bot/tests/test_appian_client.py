"""
Pruebas unitarias de AppianClient.

Todas corren sin Appian real ni navegador real: se reemplaza la clase
AppianFlow por MockAppianFlow (tests/mocks/mock_appian_flow.py), que
respeta el mismo contrato de respuestas {success, message, data}.

Cómo correr estas pruebas (ver también GUIA_MODIFICACION.md):
    cd activos_fijos_bot
    python -m pytest tests/test_appian_client.py -v
"""

from unittest.mock import patch

import pandas as pd
import pytest

from src.appian.appian_client import (
    CAMPO_ACCION_SOLICITADA,
    CAMPO_TIPO_ACTIVO,
    AppianClient,
)
from src.config.asset_type_mapping import AccionSolicitud, TipoActivo
from tests.mocks.mock_appian_flow import FakeSeleniumDriver, FakeWait, MockAppianFlow


@pytest.fixture()
def client():
    """AppianClient ya iniciado (start()) contra un MockAppianFlow."""
    with patch("src.appian.appian_client.AppianFlow", new=MockAppianFlow):
        appian_client = AppianClient(url="https://appian.fake.local")
        response = appian_client.start()
        assert response["success"] is True
        yield appian_client
        appian_client.close()


# -------------------------------------------------
# start() / close()
# -------------------------------------------------
def test_start_exitoso_crea_flow_y_llama_login(client):
    assert client._flow is not None
    assert any(call[0] == "start" for call in client._flow.calls)


def test_start_fallido_propaga_error():
    with patch("src.appian.appian_client.AppianFlow", new=MockAppianFlow), patch.object(
        MockAppianFlow,
        "start",
        return_value={"success": False, "message": "Credenciales inválidas", "data": None},
    ):
        appian_client = AppianClient(url="https://appian.fake.local")
        response = appian_client.start()

        assert response["success"] is False
        assert "Credenciales inválidas" in response["message"]


def test_start_sin_libreria_instalada_retorna_error_claro():
    # Simula el escenario real de este PC de desarrollo: la librería
    # an0016001_appian_flow no está instalada/disponible (AppianFlow es
    # None por el import protegido). Se fuerza explícitamente con patch
    # en vez de depender de que el import realmente falle, para que esta
    # prueba sea igual de válida en el PC de la empresa (donde la
    # librería real SÍ está instalada).
    with patch("src.appian.appian_client.AppianFlow", new=None):
        appian_client = AppianClient(url="https://appian.fake.local")
        response = appian_client.start()

        assert response["success"] is False
        assert "an0016001_appian_flow" in response["message"]
        assert appian_client._flow is None


def test_close_limpia_referencia_al_flow(client):
    client.close()
    assert client._flow is None


# -------------------------------------------------
# discover_pending_cases()
# -------------------------------------------------
def test_discover_pending_cases_sin_iniciar_sesion_retorna_error():
    with patch("src.appian.appian_client.AppianFlow", new=MockAppianFlow):
        appian_client = AppianClient(url="https://appian.fake.local")
        response = appian_client.discover_pending_cases()
        assert response["success"] is False
        assert "start()" in response["message"]


def test_discover_pending_cases_grilla_vacia(client):
    client._flow.driver = FakeSeleniumDriver(grid_vacia=True)
    client._flow.wait = FakeWait(client._flow.driver)

    response = client.discover_pending_cases()

    assert response["success"] is True
    assert response["data"] == []


def test_discover_pending_cases_con_solicitudes(client):
    client._flow.driver = FakeSeleniumDriver(case_links=["ABCD-1234", "ABCD-5678", "ABCD-1234"])
    client._flow.wait = FakeWait(client._flow.driver)

    response = client.discover_pending_cases()

    assert response["success"] is True
    # No debe haber duplicados aunque el link se repita en la grilla.
    assert response["data"] == ["ABCD-1234", "ABCD-5678"]


def test_discover_pending_cases_ignora_texto_que_no_parece_numero_de_caso(client):
    # Un link cuyo texto no cumple el patrón "XXX-XXX" debe ser ignorado,
    # para no confundir enlaces de navegación con números de caso reales.
    client._flow.driver = FakeSeleniumDriver(case_links=["Ver todo", "ABCD-1234"])
    client._flow.wait = FakeWait(client._flow.driver)

    response = client.discover_pending_cases()

    assert response["data"] == ["ABCD-1234"]


# -------------------------------------------------
# get_case_data() (encadena search_case + get_case_data)
# -------------------------------------------------
def test_get_case_data_exitoso_encadena_search_case(client):
    client._flow.get_case_data_response = {
        "success": True,
        "message": "OK",
        "data": {"info": pd.DataFrame([{"label": "x", "value": "y"}]), "files": []},
    }

    response = client.get_case_data("ABCD-1234")

    assert response["success"] is True
    assert ("search_case", "ABCD-1234") in client._flow.calls
    assert ("get_case_data", "ABCD-1234", True) in client._flow.calls


def test_get_case_data_no_llama_get_case_data_si_search_case_falla(client):
    client._flow.search_case_response = {
        "success": False,
        "message": "No se encontró información para el caso ABCD-9999",
        "data": None,
    }

    response = client.get_case_data("ABCD-9999")

    assert response["success"] is False
    assert not any(call[0] == "get_case_data" for call in client._flow.calls)


# -------------------------------------------------
# advance_case() (encadena search_case + advance_case)
# -------------------------------------------------
def test_advance_case_exitoso(client):
    form_data = {"Observaciones": "Procesado automáticamente por el bot"}

    response = client.advance_case("ABCD-1234", form_data)

    assert response["success"] is True
    assert ("advance_case", "ABCD-1234", form_data) in client._flow.calls


def test_advance_case_no_avanza_si_no_encuentra_el_caso(client):
    client._flow.search_case_response = {
        "success": False,
        "message": "No se encontró información para el caso ABCD-0000",
        "data": None,
    }

    response = client.advance_case("ABCD-0000", {})

    assert response["success"] is False
    assert not any(call[0] == "advance_case" for call in client._flow.calls)


# -------------------------------------------------
# parse_asset_request()
# -------------------------------------------------
def test_parse_asset_request_reconoce_tipo_y_accion(client):
    info = pd.DataFrame(
        [
            {"label": CAMPO_TIPO_ACTIVO, "value": "BRP"},
            {"label": CAMPO_ACCION_SOLICITADA, "value": "Creación"},
        ]
    )

    response = client.parse_asset_request(info)

    assert response["success"] is True
    assert response["data"]["tipo_activo"] == TipoActivo.BRP
    assert response["data"]["accion"] == AccionSolicitud.CREACION


def test_parse_asset_request_falla_si_falta_el_campo(client):
    info = pd.DataFrame([{"label": CAMPO_TIPO_ACTIVO, "value": "BRP"}])

    response = client.parse_asset_request(info)

    assert response["success"] is False
    assert CAMPO_ACCION_SOLICITADA in response["message"]


def test_parse_asset_request_falla_si_el_valor_no_esta_mapeado(client):
    info = pd.DataFrame(
        [
            {"label": CAMPO_TIPO_ACTIVO, "value": "TIPO_QUE_NO_EXISTE"},
            {"label": CAMPO_ACCION_SOLICITADA, "value": "Creación"},
        ]
    )

    response = client.parse_asset_request(info)

    assert response["success"] is False
    assert "TIPO_QUE_NO_EXISTE" in response["message"]
