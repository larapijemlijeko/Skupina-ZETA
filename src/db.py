import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager

def get_connection():
    return psycopg2.connect(
        dbname=os.environ["DBNAME"],
        user=os.environ["DBUSER"],
        password=os.environ["DBPASS"],
        host=os.environ["DBHOST"]
    )
@contextmanager
def get_db():
    """Kontekstni upravljalec za povezavo na bazo"""
    conn = None
    try:
        conn = get_connection()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def init_db():
    """Dodamo potrebne attribute tableu uporabnikov, to je narejeno tako zaradi zdruzljivosti z implementacijo ostalih funkcij"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Dodamo vrstični atribut reset_token in reset_token_expiry v tabelo 
        cur.execute("""
            ALTER TABLE uporabniki 
            ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255),
            ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMP
        """)
        
        # Ustvarimo sekundarne indekse za hitrejše poizvedbe
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_vsecki_datum 
            ON vsecki(datum_vsecka);
            
            CREATE INDEX IF NOT EXISTS idx_vsecki_recept_datum 
            ON vsecki(recept_id, datum_vsecka);
            
            CREATE INDEX IF NOT EXISTS idx_uporabniki_reset_token 
            ON uporabniki(reset_token);
        """)
        
        conn.commit()
        print("Database initialized successfully")
        
    except psycopg2.Error as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def test_connection():
    """preveri povezljivost"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"Connected to: {version}")
        cur.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"Connection test failed: {e}")
        return False