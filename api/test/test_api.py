from app.api import app
from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

def test_preview_endpoint():
    client = TestClient(app)
    # Datos de ejemplo para la prueba
    data = {
    "IP_MIKROTIK": "192.168.2.238",
    "DATE": "2023-05-25",
    "SPREADSHEET_NAME": "test!A1:B25"
}
    response = client.post("/preview", json=data)

    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Verificar que la respuesta sea una lista

    # Verificar las sublistas
    assert len(response.json()) == 2  # Verificar que hay dos sublistas
    for sublist in response.json():
        assert isinstance(sublist, list)  # Verificar que cada sublista sea una lista

        # Verificar los objetos en cada sublista
        for item in sublist:
            assert isinstance(item, dict)  # Verificar que cada elemento sea un diccionario
            assert 'comment' in item  # Verificar que el campo 'comment' esté presente
            assert 'id' in item  # Verificar que el campo 'id' esté presente


@pytest.fixture
def client():
    return TestClient(app)
@patch('app.router.routes.get_sheet_values')
@patch('app.router.routes.connect_to_mikrotik')
@patch('app.router.routes.get_addresses')
@patch('app.router.routes.add_suspended_address')
@patch('app.router.routes.suspend_address')
def test_script_route(
    mock_suspend_address,
    mock_add_suspended_address,
    mock_get_addresses,
    mock_connect_to_mikrotik,
    mock_get_sheet_values,
    client
):
    # Configurar comportamiento de las funciones mock
    mock_get_sheet_values.return_value = "sheet_list"
    mock_connect_to_mikrotik.return_value = "api"
    mock_get_addresses.return_value = "addr_list_ip"
    mock_add_suspended_address.return_value = "addr_list_updated"

    # Hacer una solicitud a la ruta /script
    response = client.post("/script", json={})

    # Verificar que se llamaron a las funciones esperadas con los argumentos correctos
    mock_get_sheet_values.assert_called_once_with({})
    mock_connect_to_mikrotik.assert_called_once_with({})
    mock_get_addresses.assert_called_once_with("api", "sheet_list")
    mock_add_suspended_address.assert_called_once_with("addr_list_ip", "sheet_list", "api")
    mock_suspend_address.assert_called_once_with("api", "sheet_list", "addr_list_updated", {})

    # Verificar la respuesta de la solicitud
    assert response.status_code == 200
    assert response.json() == {"message": "done"}
