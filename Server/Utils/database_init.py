from Utils.database_connection import get_connection


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        address TEXT NOT NULL,
        card_number TEXT NOT NULL
    )
    ''')

    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY,
        car_plate TEXT NOT NULL UNIQUE,
        doors INTEGER NOT NULL,
        fuel INTEGER NOT NULL CHECK(fuel >= 0 AND fuel <= 100),
        registration_number TEXT NOT NULL,
        available BOOLEAN NOT NULL,
        lights BOOLEAN NOT NULL,
        locked BOOLEAN NOT NULL,
        car_port INTEGER NOT NULL UNIQUE
    )''')

    conn.commit()

