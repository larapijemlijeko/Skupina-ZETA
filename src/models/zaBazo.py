# src/models/zaBazo.py

import db
import psycopg2

# Uvoz funkcij za ustvarjanje tabel
from . import uporabniki, recepti, sestavine, oznake, favourite, vsecki, nagradneigre

def create_tables():
    """Ustvari vse potrebne tabele v bazi, če še ne obstajajo."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()

        print("Vzpostavljena povezava z bazo.")

       

        # Klici funkcij iz posameznih modelov
        uporabniki.create_table(cur)
        recepti.create_table(cur)
        sestavine.create_table(cur)
        oznake.create_table(cur)
        favourite.create_table(cur)
        vsecki.create_table(cur)
        nagradneigre.create_table(cur)

        conn.commit()
        print("Tabele so bile uspešno ustvarjene.")

    except (psycopg2.Error, Exception) as e:
        print(f"Napaka pri ustvarjanju tabel: {e}")
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()
            print("Povezava z bazo je zaprta.")
