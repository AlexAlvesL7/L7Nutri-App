import pytest
from app import app, db, Usuario

def test_usuario_cadastro():
    tester = app.test_client()
    payload = {
        "username": "pytest_user",
        "password": "pytest123",
        "idade": 25,
        "sexo": "feminino",
        "peso": 65,
        "altura": 170,
        "nivel_atividade": "ativo",
        "objetivo": "perder"
    }
    response = tester.post('/cadastro', json=payload)
    assert response.status_code in [201, 409]
    data = response.get_json()
    assert "message" in data
    # Limpeza
    if response.status_code == 201:
        user = Usuario.query.filter_by(username="pytest_user").first()
        if user:
            db.session.delete(user)
            db.session.commit()
