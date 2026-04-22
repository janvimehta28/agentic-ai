import pytest
from fastapi.testclient import TestClient
from main import app, get_user, verify_password, get_password_hash, create_access_token, login
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import decode

# Create a test client
client = TestClient(app)

class User(BaseModel):
    """User model"""
    username: str
    password: str

class Token(BaseModel):
    """Token model"""
    access_token: str
    token_type: str

# Test the get_user function
def test_get_user():
    """
    Test the get_user function.

    Verifies:
    - The function returns a user if the username exists in the database.
    - The function returns None if the username does not exist in the database.
    """
    # Create a test user
    users_db = {}
    users_db["test_user"] = "test_password"
    
    # Test the function with an existing user
    user = get_user("test_user")
    assert user is not None
    assert user.username == "test_user"
    assert user.password == "test_password"
    
    # Test the function with a non-existent user
    user = get_user("non_existent_user")
    assert user is None

# Test the verify_password function
def test_verify_password():
    """
    Test the verify_password function.

    Verifies:
    - The function returns True if the password is valid.
    - The function returns False if the password is invalid.
    """
    # Create a test user
    users_db = {}
    users_db["test_user"] = get_password_hash("test_password")
    
    # Test the function with a valid password
    assert verify_password("test_password", users_db["test_user"]) is True
    
    # Test the function with an invalid password
    assert verify_password("invalid_password", users_db["test_user"]) is False

# Test the get_password_hash function
def test_get_password_hash():
    """
    Test the get_password_hash function.

    Verifies:
    - The function returns a hashed password.
    """
    # Test the function
    hashed_password = get_password_hash("test_password")
    assert hashed_password is not None

# Test the create_access_token function
def test_create_access_token():
    """
    Test the create_access_token function.

    Verifies:
    - The function returns an access token.
    """
    # Test the function
    access_token = create_access_token(data={"sub": "test_user"})
    assert access_token is not None

# Test the login function
def test_login():
    """
    Test the login function.

    Verifies:
    - The function returns a token if the login is successful.
    - The function raises an exception if the login is unsuccessful.
    """
    # Create a test user
    users_db = {}
    users_db["test_user"] = get_password_hash("test_password")
    
    # Test the function with valid credentials
    token = login("test_user", "test_password")
    assert token is not None
    assert token.access_token is not None
    assert token.token_type == "bearer"
    
    # Test the function with invalid credentials
    with pytest.raises(Exception):
        login("test_user", "invalid_password")

# Test the login endpoint
def test_login_endpoint():
    """
    Test the login endpoint.

    Verifies:
    - The endpoint returns a token if the login is successful.
    - The endpoint raises an exception if the login is unsuccessful.
    """
    # Create a test user
    users_db = {}
    users_db["test_user"] = get_password_hash("test_password")
    
    # Test the endpoint with valid credentials
    response = client.post("/login", data={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200
    assert response.json()["access_token"] is not None
    assert response.json()["token_type"] == "bearer"
    
    # Test the endpoint with invalid credentials
    response = client.post("/login", data={"username": "test_user", "password": "invalid_password"})
    assert response.status_code == 401

# Test the login endpoint with None inputs
def test_login_endpoint_none_inputs():
    """
    Test the login endpoint with None inputs.

    Verifies:
    - The endpoint raises an exception if the username or password is None.
    """
    # Test the endpoint with None username
    response = client.post("/login", data={"username": None, "password": "test_password"})
    assert response.status_code == 422
    
    # Test the endpoint with None password
    response = client.post("/login", data={"username": "test_user", "password": None})
    assert response.status_code == 422

# Test the login endpoint with empty strings
def test_login_endpoint_empty_strings():
    """
    Test the login endpoint with empty strings.

    Verifies:
    - The endpoint raises an exception if the username or password is an empty string.
    """
    # Test the endpoint with empty username
    response = client.post("/login", data={"username": "", "password": "test_password"})
    assert response.status_code == 401
    
    # Test the endpoint with empty password
    response = client.post("/login", data={"username": "test_user", "password": ""})
    assert response.status_code == 401

# Test the login endpoint with boundary values
def test_login_endpoint_boundary_values():
    """
    Test the login endpoint with boundary values.

    Verifies:
    - The endpoint raises an exception if the username or password exceeds the maximum length.
    """
    # Test the endpoint with long username
    response = client.post("/login", data={"username": "a" * 1000, "password": "test_password"})
    assert response.status_code == 422
    
    # Test the endpoint with long password
    response = client.post("/login", data={"username": "test_user", "password": "a" * 1000})
    assert response.status_code == 422

# Test the login endpoint with type errors
def test_login_endpoint_type_errors():
    """
    Test the login endpoint with type errors.

    Verifies:
    - The endpoint raises an exception if the username or password is not a string.
    """
    # Test the endpoint with non-string username
    response = client.post("/login", data={"username": 123, "password": "test_password"})
    assert response.status_code == 422
    
    # Test the endpoint with non-string password
    response = client.post("/login", data={"username": "test_user", "password": 123})
    assert response.status_code == 422