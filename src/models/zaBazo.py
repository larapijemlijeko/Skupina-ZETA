import db
import psycopg2

# Uvoz funkcij za ustvarjanje tabel
from . import uporabniki, recepti, sestavine, oznake, favourite, vsecki, nagradneigre, scraped, faq, nagradnaigra, zakalorije

def create_tables():
    """Ustvari vse potrebne tabele v bazi, če še ne obstajajo."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        print("Vzpostavljena povezava z bazo.")

       

        # Ustvari tabele
        uporabniki.create_table(cur)
        recepti.create_table(cur)
        sestavine.create_table(cur)
        oznake.create_table(cur)
        favourite.create_table(cur)
        vsecki.create_table(cur)
        nagradneigre.create_table(cur)
        scraped.create_table(cur)
        faq.create_faq_table(cur)
        nagradnaigra.create_table(cur)
        zakalorije.create_user_data_table(cur)

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
