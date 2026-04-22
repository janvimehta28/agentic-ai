# Import required libraries
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jwt import encode, decode
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Define the FastAPI application
app = FastAPI()

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Define the user model
class User(BaseModel):
    """User model"""
    username: str
    password: str

# Define the token model
class Token(BaseModel):
    """Token model"""
    access_token: str
    token_type: str

# Define the password context
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

# Define the users database (in-memory for simplicity)
users_db: Dict[str, str] = {}

def get_user(username: str) -> Optional[User]:
    """
    Get a user from the database.

    Args:
    - username (str): The username to retrieve.

    Returns:
    - Optional[User]: The user if found, None otherwise.
    """
    # Check if the username exists in the database
    if username in users_db:
        # Return the user
        return User(username=username, password=users_db[username])
    else:
        # Return None if the user is not found
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.

    Args:
    - plain_password (str): The plain password to verify.
    - hashed_password (str): The hashed password to verify against.

    Returns:
    - bool: True if the password is valid, False otherwise.
    """
    # Use the password context to verify the password
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Get the hashed password.

    Args:
    - password (str): The password to hash.

    Returns:
    - str: The hashed password.
    """
    # Use the password context to hash the password
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, str], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an access token.

    Args:
    - data (Dict[str, str]): The data to encode in the token.
    - expires_delta (Optional[timedelta]): The expiration time delta. Defaults to None.

    Returns:
    - str: The access token.
    """
    # Set the expiration time if not provided
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # Create the token payload
    payload = data.copy()
    payload.update({"exp": expire})
    
    # Encode the payload to create the token
    return encode(payload, "secret_key", algorithm="HS256")

def login(username: str, password: str) -> Optional[Token]:
    """
    Login a user.

    Args:
    - username (str): The username to login.
    - password (str): The password to login with.

    Returns:
    - Optional[Token]: The token if the login is successful, None otherwise.
    """
    # Get the user from the database
    user = get_user(username)
    
    # Check if the user exists
    if not user:
        # Raise an exception if the user is not found
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify the password
    if not verify_password(password, user.password):
        # Raise an exception if the password is invalid
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create the access token
    access_token = create_access_token(data={"sub": username})
    
    # Return the token
    return Token(access_token=access_token, token_type="bearer")

# Define the login endpoint
@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint.

    Args:
    - form_data (OAuth2PasswordRequestForm): The login form data.

    Returns:
    - Token: The access token.
    """
    # Login the user
    return login(form_data.username, form_data.password)

# Define a test user
@app.on_event("startup")
async def startup_event():
    # Create a test user
    users_db["test_user"] = get_password_hash("test_password")