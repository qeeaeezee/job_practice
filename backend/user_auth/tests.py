import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

import pytest
from ninja.testing import TestClient
from job_platform.api import api
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

test_client = TestClient(api)

@pytest.fixture
def client():
    return test_client

@pytest.fixture
def test_user_data():
    return {
        "username": "testuser", 
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }

@pytest.mark.django_db
def test_user_registration_success(client, test_user_data):
    """測試用戶註冊成功"""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201, response.content
    
    result = response.json()
    assert "access" in result
    assert "refresh" in result
    
    # 驗證用戶已創建
    user = User.objects.get(username=test_user_data["username"])
    assert user.email == test_user_data["email"]
    assert user.first_name == test_user_data["first_name"]
    assert user.last_name == test_user_data["last_name"]

@pytest.mark.django_db
def test_user_registration_duplicate_username(client, test_user_data):
    """測試重複用戶名註冊失敗"""
    User.objects.create_user(
        username=test_user_data["username"],
        email="different@example.com",
        password="password123"
    )
    
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert response.json()["message"] == "Username already exists"

@pytest.mark.django_db
def test_user_registration_duplicate_email(client, test_user_data):
    """測試重複 email 註冊失敗"""
    User.objects.create_user(
        username="differentuser",
        email=test_user_data["email"],
        password="password123"
    )
    
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert response.json()["message"] == "Email already exists"

@pytest.mark.django_db
def test_user_login_success(client):
    """測試用戶登入成功"""
    User.objects.create_user(
        username="testuser",
        password="testpassword123"
    )
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200, response.content
    
    result = response.json()
    assert "access" in result
    assert "refresh" in result

@pytest.mark.django_db
def test_user_login_invalid_credentials(client):
    """測試無效憑證登入失敗"""
    # 先創建用戶
    User.objects.create_user(
        username="testuser",
        password="testpassword123"
    )
    
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid credentials"

@pytest.mark.django_db
def test_user_login_nonexistent_user(client):
    """測試不存在的用戶登入失敗"""
    login_data = {
        "username": "nonexistent",
        "password": "password123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid credentials"

@pytest.mark.django_db
def test_user_login_inactive_user(client):
    """測試已停用用戶登入失敗"""
    # 創建已停用的用戶
    user = User.objects.create_user(
        username="testuser",
        password="testpassword123"
    )
    user.is_active = False
    user.save()
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["message"] == "Account is disabled"

@pytest.mark.django_db
def test_token_refresh_success(client):
    """測試 token 更新成功"""
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 201
    
    tokens = response.json()
    refresh_token = tokens["refresh"]
    
    # 使用 refresh token 獲取新的 access token
    refresh_data = {"refresh": refresh_token}
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    
    result = response.json()
    assert "access" in result

@pytest.mark.django_db
def test_token_refresh_invalid_token(client):
    """測試無效 refresh token 更新失敗"""
    refresh_data = {"refresh": "invalid_token"}
    response = client.post("/auth/refresh", json=refresh_data)
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid refresh token"

@pytest.mark.django_db
def test_jwt_protected_endpoint_without_token(client):
    """測試沒有 token 訪問受保護端點失敗"""
    expiration_date = timezone.now() + timedelta(days=30)
    job_data = {
        "title": "Test Job",
        "description": "Test Description",
        "location": "Remote",
        "salary_range": "100k-150k USD",
        "company_name": "Test Company",
        "expiration_date": expiration_date.isoformat(),
        "required_skills": ["Python"],
        "is_scheduled": False,
    }
    
    response = client.post("/jobs", json=job_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

@pytest.mark.django_db
def test_jwt_protected_endpoint_with_valid_token(client):
    """測試使用有效 token 訪問受保護端點成功"""
    # 先註冊並登入獲取 token
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 201
    
    tokens = response.json()
    access_token = tokens["access"]
    
    # 使用 token 訪問受保護端點
    expiration_date = timezone.now() + timedelta(days=30)
    job_data = {
        "title": "Test Job",
        "description": "Test Description",
        "location": "Remote",
        "salary_range": "100k-150k USD",
        "company_name": "Test Company",
        "expiration_date": expiration_date.isoformat(),
        "required_skills": ["Python"],
        "is_scheduled": False,
    }
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/jobs", json=job_data, headers=headers)
    assert response.status_code == 201

@pytest.mark.django_db
def test_jwt_protected_endpoint_with_invalid_token(client):
    """測試使用無效 token 訪問受保護端點失敗"""
    expiration_date = timezone.now() + timedelta(days=30)
    job_data = {
        "title": "Test Job",
        "description": "Test Description",
        "location": "Remote",
        "salary_range": "100k-150k USD",
        "company_name": "Test Company",
        "expiration_date": expiration_date.isoformat(),
        "required_skills": ["Python"],
        "is_scheduled": False,
    }
    
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/jobs", json=job_data, headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
