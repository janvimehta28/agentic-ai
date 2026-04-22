# Import required libraries
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta

# Define the FastAPI application
app = FastAPI()

# Define the security scheme for basic authentication
security = HTTPBasic()

# Define a model for the user credentials
class UserCredentials(BaseModel):
    """Model for user credentials."""
    username: str
    password: str

# Define a model for the user
class User(BaseModel):
    """Model for a user."""
    id: int
    username: str
    password: str

# In-memory database for demonstration purposes
# In a real application, use a proper database
users_db: Dict[int, User] = {
    1: User(id=1, username="user1", password="password1"),
    2: User(id=2, username="user2", password="password2"),
}

def get_user(username: str) -> Optional[User]:
    """
    Retrieves a user from the database by username.

    Args:
    - username (str): The username to search for.

    Returns:
    - Optional[User]: The user if found, otherwise None.
    """
    # Iterate over the users in the database
    for user in users_db.values():
        # Check if the username matches
        if user.username == username:
            # Return the user if found
            return user
    # Return None if not found
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    Args:
    - plain_password (str): The plain password to verify.
    - hashed_password (str): The hashed password to compare against.

    Returns:
    - bool: True if the passwords match, False otherwise.
    """
    # For demonstration purposes, assume the hashed password is the plain password
    # In a real application, use a proper password hashing algorithm
    return plain_password == hashed_password

def generate_jwt_token(user: User) -> str:
    """
    Generates a JWT token for a user.

    Args:
    - user (User): The user to generate the token for.

    Returns:
    - str: The generated JWT token.
    """
    # Set the token expiration time to 1 hour
    expiration_time = datetime.utcnow() + timedelta(hours=1)
    # Create a payload for the token
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": int(expiration_time.timestamp())
    }
    # Generate the token using a secret key
    # In a real application, use a secure secret key
    secret_key = "secret_key"
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    # Return the generated token
    return token

@app.post("/login")
def login(credentials: UserCredentials) -> Dict[str, str]:
    """
    Handles the login endpoint.

    Args:
    - credentials (UserCredentials): The user credentials.

    Returns:
    - Dict[str, str]: A dictionary containing the JWT token.
    """
    # Retrieve the user from the database
    user = get_user(credentials.username)
    # Check if the user exists
    if user is None:
        # Raise an exception if the user does not exist
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Verify the password
    if not verify_password(credentials.password, user.password):
        # Raise an exception if the password is incorrect
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # Generate a JWT token for the user
    token = generate_jwt_token(user)
    # Return the token in a dictionary
    return {"token": token}