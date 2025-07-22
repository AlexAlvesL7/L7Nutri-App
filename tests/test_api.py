import pytest
from app import app

def test_home_status_code():
    tester = app.test_client()
    response = tester.get("/")
    assert response.status_code == 200
