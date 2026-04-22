# Import required libraries
import sqlite3
from typing import Tuple, Optional
from sqlite3 import Error

# Define a function to create a connection to the SQLite database
def create_connection(db_file: str) -> Optional[sqlite3.Connection]:
    """
    Create a connection to the SQLite database.

    Args:
    db_file (str): The path to the SQLite database file.

    Returns:
    Optional[sqlite3.Connection]: The connection object or None if the connection fails.
    """
    if db_file is None:
        return None
    if not isinstance(db_file, str):
        raise TypeError("db_file must be a string path")
    if db_file.strip() == "":
        return None

    try:
        # Attempt to establish a connection to the SQLite database
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        # Handle any errors that occur during connection establishment
        print(f"Error occurred while creating connection: {e}")
        return None


# Define a function to validate the username and password against the database
def validate_credentials(conn: sqlite3.Connection, username: str, password: str) -> bool:
    """
    Validate the username and password against the database.

    Args:
    conn (sqlite3.Connection): The connection object to the SQLite database.
    username (str): The username to validate.
    password (str): The password to validate.

    Returns:
    bool: True if the credentials are valid, False otherwise.
    """
    if username is None or password is None:
        return False
    if not isinstance(username, str) or not isinstance(password, str):
        raise TypeError("username and password must be strings")
    if username == "" or password == "":
        return False

    try:
        # Create a cursor object to execute SQL queries
        cur = conn.cursor()
        
        # Query the users table to check if the username and password match
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        
        # Fetch the result of the query
        result = cur.fetchone()
        
        # If a result is found, the credentials are valid
        if result:
            return True
        else:
            return False
    except Error as e:
        # Handle any errors that occur during query execution
        print(f"Error occurred while validating credentials: {e}")
        return False


# Define a function to handle the login endpoint
def handle_login(conn: sqlite3.Connection, username: str, password: str) -> Tuple[bool, str]:
    """
    Handle the login endpoint by validating the username and password.

    Args:
    conn (sqlite3.Connection): The connection object to the SQLite database.
    username (str): The username to validate.
    password (str): The password to validate.

    Returns:
    Tuple[bool, str]: A tuple containing a boolean indicating whether the login was successful and a message.
    """
    if username is None or password is None:
        return False, "Invalid username or password"
    if not isinstance(username, str) or not isinstance(password, str):
        raise TypeError("username and password must be strings")
    if username == "" or password == "":
        return False, "Invalid username or password"

    # Validate the username and password
    if validate_credentials(conn, username, password):
        # If the credentials are valid, return a success message
        return True, "Login successful"
    else:
        # If the credentials are invalid, return an error message
        return False, "Invalid username or password"


# Define a main function to demonstrate the usage of the login endpoint
def main():
    # Create a connection to the SQLite database
    conn = create_connection("users.db")
    
    # Check if the connection was established successfully
    if conn:
        # Handle the login endpoint with example credentials
        login_result, message = handle_login(conn, "example_username", "example_password")
        
        # Print the result of the login attempt
        print(f"Login result: {login_result}, Message: {message}")
        
        # Close the connection to the database
        conn.close()
    else:
        print("Failed to establish connection to the database")


if __name__ == "__main__":
    main()