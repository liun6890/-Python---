import pymysql

# Database connection parameters
HOST = 'localhost'
USER = 'root'
PASSWORD = '123456'
DB_NAME = 'wms'
PORT = 3306

try:
    # Connect to MySQL server (without selecting a database)
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        port=PORT
    )
    cursor = connection.cursor()

    # Create database if it doesn't exist
    print(f"Checking database '{DB_NAME}'...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print(f"Database '{DB_NAME}' created or already exists.")

    connection.commit()
    cursor.close()
    connection.close()

except pymysql.MySQLError as e:
    print(f"Error connecting to MySQL: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
