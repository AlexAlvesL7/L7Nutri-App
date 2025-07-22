import pytest
from app import app

def test_api_teste():
    tester = app.test_client()
    response = tester.get('/api/teste-tabelas')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'success'
    assert 'usuarios_cadastrados' in data
    assert 'tabela_acessivel' in data
    assert data['tabela_acessivel'] is True
