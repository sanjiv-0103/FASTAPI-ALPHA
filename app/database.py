
# 1. Import Libraries
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# 2. Load Environment Variables
load_dotenv()

# 3. Connect to PostgreSQL
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT","5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )

# 4. Test Database Connection
def test_connection():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT current_database(),current_user")
                result=cursor.fetchone()
                print("PostgreSQL connected successfully!")
                print("Database:",result["current_database"])
                print("User:",result["current_user"])
    except psycopg2.Error as error:
        print("Database connection failed!")
        print("Error:",error)

# 5. Run Connection Test
if __name__=="__main__":
    test_connection()
