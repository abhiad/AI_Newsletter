import sqlite3
 
 
# Function to create a connection to the SQLite database

def create_connection():

    try:

        connection = sqlite3.connect("newsletter.db")  # SQLite database file

        return connection

    except sqlite3.Error as e:

        print(f"Error: Unable to connect to the database. {e}")

        return None
 
 
def close_connection(connection):

    if connection:

        connection.close()
 
 
def execute_non_select(query, params=None):

    conn = create_connection()

    if conn is None:

        return False

    try:

        with conn:

            cursor = conn.cursor()

            cursor.execute(query, params or [])

        return True

    except sqlite3.Error as e:

        print(f"Error executing query: {e}")

        return False

    finally:

        close_connection(conn)
 
 
def execute_select(query, params=None):

    conn = create_connection()

    if conn is None:

        return []

    try:

        with conn:

            cursor = conn.cursor()

            cursor.execute(query, params or [])

            return cursor.fetchall()

    except sqlite3.Error as e:

        print(f"Error executing select: {e}")

        return []

    finally:

        close_connection(conn)
 
 
# Create only the users table

def init_db():

    execute_non_select('''

        CREATE TABLE IF NOT EXISTS users (

            email TEXT PRIMARY KEY,

            subscribed BOOLEAN NOT NULL

        )

    ''')
 
 
# Save or update user subscription

def save_user(email, subscribed):

    return execute_non_select('''

        INSERT INTO users (email, subscribed)

        VALUES (?, ?)

        ON CONFLICT(email) DO UPDATE SET subscribed = excluded.subscribed

    ''', (email, subscribed))
 
 
# Update existing user subscription only

def update_subscription_status(email, subscribed):

    return execute_non_select('''

        UPDATE users

        SET subscribed = ?

        WHERE email = ?

    ''', (subscribed, email))
 
 
# Check if user is subscribed

def is_user_subscribed(email):

    result = execute_select('SELECT subscribed FROM users WHERE email = ?', (email,))

    if result:

        return result[0][0]

    return False
 
 
# Get list of all subscribed users

def get_subscribed_users():

    results = execute_select('SELECT email FROM users WHERE subscribed = 1')

    return [row[0] for row in results]
 
 
# Initialize database when module loads

init_db()
 
