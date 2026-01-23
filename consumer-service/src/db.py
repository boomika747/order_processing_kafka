import psycopg2, os

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
conn.autocommit = True
