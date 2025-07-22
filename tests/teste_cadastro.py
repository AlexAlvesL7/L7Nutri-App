import pytest
from app import app, db, Usuario

def test_cadastro_usuario():
    tester = app.test_client()
    # Dados de teste
    payload = {
        "username": "testuser_pytest",
        "password": "12345678",
        "idade": 30,
        "sexo": "masculino",
        "peso": 80,
        "altura": 180,
        "nivel_atividade": "moderadamente_ativo",
        "objetivo": "manter"
    }
    response = tester.post('/cadastro', json=payload)
    assert response.status_code in [201, 409]  # 409 se já existe
    data = response.get_json()
    assert "message" in data
    # Limpeza: remove usuário criado (se criado)
    if response.status_code == 201:
        user = Usuario.query.filter_by(username="testuser_pytest").first()
        if user:
            db.session.delete(user)
            db.session.commit()
