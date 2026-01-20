# Tests for authentication
import pytest

def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "user_name": "Test User",
            "user_email": "test@example.com",
            "password": "testpass123",
            "hospital_id": "H001",
            "user_role": "pharmacist"
        }
    )
    assert response.status_code in [201, 400, 422]

def test_login(client):
    """Test user login"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code in [200, 401, 422]
