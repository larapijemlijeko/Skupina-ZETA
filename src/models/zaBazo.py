from db import get_connection

def create_tables():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Tabela za uporabnike (če še ne obstaja)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uporabniki (
                id SERIAL PRIMARY KEY,
                uporabnisko_ime VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                geslo VARCHAR(255) NOT NULL,
                datum_registracije TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Tabela za recepte (z eno sliko)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recepti (
                id SERIAL PRIMARY KEY,
                naslov VARCHAR(100) NOT NULL,
                opis TEXT,
                priprava TEXT NOT NULL,
                cas_priprave INTEGER,
                tezavnost VARCHAR(20),
                kategorija VARCHAR(50),
                slika_url VARCHAR(255),
                uporabnik_id INTEGER REFERENCES uporabniki(id),
                datum_kreiranja TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Tabela za sestavine
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sestavine (
                id SERIAL PRIMARY KEY,
                recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
                ime VARCHAR(50) NOT NULL,
                kolicina VARCHAR(50),
                enota VARCHAR(20)
            )
        """)
        
        # 4. Tabela za oznake
        cur.execute("""
            CREATE TABLE IF NOT EXISTS oznake (
                id SERIAL PRIMARY KEY,
                recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
                oznaka VARCHAR(30) NOT NULL
            )
        """)
        
        conn.commit()
        print("Tabele so bile uspešno ustvarjene.")
    except Exception as e:
        print(f"Napaka pri ustvarjanju tabel: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# Pokličemo funkcijo za ustvarjanje tabel
create_tables()