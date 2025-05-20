# src/models/zaBazo.py

import db
import psycopg2

def create_tables():
    """Ustvari vse potrebne tabele v bazi, če še ne obstajajo."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        print("Vzpostavljena povezava z bazo.")

        # 1. Tabela za uporabnike
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uporabniki (
                id SERIAL PRIMARY KEY,
                uporabnisko_ime VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                geslo VARCHAR(255) NOT NULL,
                datum_registracije TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Tabela za recepte
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recepti (
                id SERIAL PRIMARY KEY,
                naslov VARCHAR(100) NOT NULL,
                opis TEXT,
                priprava TEXT NOT NULL,
                cas_priprave INTEGER,
                tezavnost INT,
                slika_url VARCHAR(255),
                uporabnik_id INTEGER REFERENCES uporabniki(id),
                datum_kreiranja TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # # 3. Tabela za sestavine
        # cur.execute("""
        #     CREATE TABLE IF NOT EXISTS sestavine (
        #         id SERIAL PRIMARY KEY,
        #         recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
        #         ime VARCHAR(50) NOT NULL,
        #         kolicina VARCHAR(50),
        #         enota VARCHAR(20)
        #     );
        # """)

        # # 4. Tabela za oznake
        # cur.execute("""
        #     CREATE TABLE IF NOT EXISTS oznake (
        #         id SERIAL PRIMARY KEY,
        #         recept_id INTEGER NOT NULL REFERENCES recepti(id) ON DELETE CASCADE,
        #         oznaka VARCHAR(30) NOT NULL
        #     );
        # """)

        # # 5. Tabela za priljubljene (favourite)
        # cur.execute("""
        #     CREATE TABLE IF NOT EXISTS favourite (
        #         id SERIAL PRIMARY KEY,
        #         title VARCHAR(50),
        #         url VARCHAR(100),
        #         uporabnik_id INTEGER REFERENCES uporabniki(id)
        #     );
        # """)
        # # 6. Tabela za prijavo na nagradne igre
        cur.execute("""
           CREATE TABLE IF NOT EXISTS nagradne_prijave (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            prijavljen_ob TIMESTAMP DEFAULT CURRENT_TIMESTAMP
             );
            """)


        conn.commit()
        print(" Tabele so bile uspešno ustvarjene.")

    except (psycopg2.Error, Exception) as e:
        print(f" Napaka pri ustvarjanju tabel: {e}")
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()
            print("Povezava z bazo je zaprta.")
