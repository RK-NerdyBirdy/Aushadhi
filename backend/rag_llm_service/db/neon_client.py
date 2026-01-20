import psycopg2
import psycopg2.extras
from config.settings import DATABASE_URL


class NeonClient:
    def fetch_one(self, query, params=None):
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cur:
                cur.execute(query, params)
                return cur.fetchone()

    def fetch_all(self, query, params=None):
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cur:
                cur.execute(query, params)
                return cur.fetchall()
