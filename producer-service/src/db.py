from contextlib import contextmanager
import psycopg2
import os

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.autocommit = True
        yield conn
    finally:
        if conn:
            conn.close()
