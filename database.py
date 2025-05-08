import psycopg2
from psycopg2 import OperationalError


# Function to create a connection to the PostgreSQL database
def create_connection():
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="s10mbv9",
            password="postgres",
            host="db.lczwidaqgmwlxcfewbso.supabase.co",
            port="5432"
        )
        return connection
    except OperationalError as e:
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
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error executing query: {e}")
        return False
    finally:
        close_connection(conn)


def execute_select(query, params=None):
    conn = create_connection()
    if conn is None:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"Error executing select: {e}")
        return []
    finally:
        close_connection(conn)


# Create only the users table
def init_db():
    execute_non_select('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           email
                           TEXT
                           PRIMARY
                           KEY,
                           subscribed
                           BOOLEAN
                           NOT
                           NULL
                       )''')


# Save or update user subscription
def save_user(email, subscribed):
    return execute_non_select('''
                              INSERT INTO users (email, subscribed)
                              VALUES (%s, %s) ON CONFLICT (email) DO
                              UPDATE SET subscribed = EXCLUDED.subscribed
                              ''', (email, subscribed))


# Update existing user subscription only
def update_subscription_status(email, subscribed):
    return execute_non_select('''
                              UPDATE users
                              SET subscribed = %s
                              WHERE email = %s
                              ''', (subscribed, email))


# Check if user is subscribed
def is_user_subscribed(email):
    result = execute_select('SELECT subscribed FROM users WHERE email = %s', (email,))
    if result:
        return result[0][0]
    return False


# Get list of all subscribed users
def get_subscribed_users():
    results = execute_select('SELECT email FROM users WHERE subscribed = TRUE')
    return [row[0] for row in results]


# Initialize database when module loads
init_db()


