import psycopg2

def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fintrack_db",
            user="postgres",        
            password="pass123" 
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None
