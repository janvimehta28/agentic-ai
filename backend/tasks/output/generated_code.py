```python
# Import required libraries
import sqlite3
from typing import Dict

# Define a function to create a connection to the SQLite database
def create_connection(database_name: str) -> sqlite3.Connection:
    """
    Create a connection to the SQLite database.

    Args:
    database_name (str): The name of the SQLite database file.

    Returns:
    sqlite3.Connection: A connection to the SQLite database.
    """
    # Connect to the SQLite database
    connection = sqlite3.connect(database_name)
    return connection

# Define a function to validate user credentials
def validate_credentials(connection: sqlite3.Connection, username: str, password: str) -> bool:
    """
    Validate user credentials against the SQLite database.

    Args:
    connection (sqlite3.Connection): A connection to the SQLite database.
    username (str): The username to validate.
    password (str): The password to validate.

    Returns:
    bool: True if the credentials are valid, False otherwise.
    """
    # Create a cursor object to execute SQL queries
    cursor = connection.cursor()
    
    # Query the database for the username and password
    # Assuming a table named 'users' with columns 'username' and 'password'
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    
    # Fetch the query result
    result = cursor.fetchone()
    
    # If a result is found, the credentials are valid
    if result:
        return True
    else:
        return False

# Define a function to handle the login endpoint
def login_endpoint(username: str, password: str, database_name: str) -> Dict[str, bool]:
    """
    Handle the login endpoint by validating user credentials.

    Args:
    username (str): The username to validate.
    password (str): The password to validate.
    database_name (str): The name of the SQLite database file.

    Returns:
    Dict[str, bool]: A dictionary with a single key 'success' and a boolean value indicating whether the login was successful.
    """
    # Create a connection to the database
    connection = create_connection(database_name)
    
    # Validate the user credentials
    is_valid = validate_credentials(connection, username, password)
    
    # Close the database connection
    connection.close()
    
    # Return the result as a dictionary
    return {'success': is_valid}

# Example usage
if __name__ == "__main__":
    database_name = "example.db"
    username = "example_user"
    password = "example_password"
    
    # Create a table in the database for demonstration purposes
    connection = create_connection(database_name)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?)", (username, password))
    connection.commit()
    connection.close()
    
    result = login_endpoint(username, password, database_name)
    print(result)
```