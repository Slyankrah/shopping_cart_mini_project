import psycopg2

# DB credentials
DB_HOST = 'localhost'
DB_NAME = 'shopping_cart'
DB_USER = 'admin'
DB_PASSWORD = 'admin123'

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    print("✅ Connection successful!")
    conn.close()
except psycopg2.Error as e:
    print("❌ Connection failed.")
    print("Error:", e)
