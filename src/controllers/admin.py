from flask import Blueprint, render_template, redirect, url_for
from models.dbBackup import createBackup
import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_panel():
    return render_template('admin.html')
@admin_bp.route('/admin/dodaj')

@admin_bp.route('/admin/dodaj')
def dodaj_testne_podatke():
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        # Preveri ali uporabnik že obstaja
        cur.execute("SELECT id FROM uporabniki WHERE uporabnisko_ime = 'adminuser'")
        uporabnik = cur.fetchone()
        if uporabnik:
            uporabnik_id = uporabnik[0]
        else:
            cur.execute("""
                INSERT INTO uporabniki (uporabnisko_ime, email, geslo)
                VALUES ('adminuser', 'admin@example.com', 'admin123')
                RETURNING id;
            """)
            uporabnik_id = cur.fetchone()[0]

        # Podatki za 4 recepte
        recepti = [
            ("Testni recept 1", "Opis 1", "Navodila 1", 15, 1, "", "Sol", "1", "žlička", "Testna1"),
            ("Testni recept 2", "Opis 2", "Navodila 2", 25, 2, "", "Poper", "2", "žlički", "Testna2"),
            ("Testni recept 3", "Opis 3", "Navodila 3", 30, 3, "", "Moka", "100", "g", "Testna3"),
            ("Testni recept 4", "Opis 4", "Navodila 4", 10, 1, "", "Voda", "2", "dl", "Testna4"),
        ]

        for naslov, opis, priprava, cas, tezavnost, slika, sest_ime, kolicina, enota, oznaka in recepti:
            cur.execute("""
                INSERT INTO recepti (naslov, opis, priprava, cas_priprave, tezavnost, slika_url, uporabnik_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (naslov, opis, priprava, cas, tezavnost, slika, uporabnik_id))
            recept_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO sestavine (recept_id, ime, kolicina, enota)
                VALUES (%s, %s, %s, %s);
            """, (recept_id, sest_ime, kolicina, enota))

            cur.execute("""
                INSERT INTO oznake (recept_id, oznaka)
                VALUES (%s, %s);
            """, (recept_id, oznaka))

        conn.commit()
        print("✅ Testni podatki uspešno dodani.")
    except Exception as e:
        conn.rollback()
        print("❌ Napaka pri dodajanju testnih podatkov:", e)
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/izbrisi_podatke')
def izbrisi_vse_podatke():
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM oznake;")
        cur.execute("DELETE FROM sestavine;")
        cur.execute("DELETE FROM recepti;")
        cur.execute("DELETE FROM uporabniki;")
        cur.execute("DELETE FROM vsecki;")
        cur.execute("DELETE FROM favourite;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Napaka:", e)
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/izbrisi_tabele')
def izbrisi_tabele():
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DROP TABLE IF EXISTS oznake CASCADE;")
        cur.execute("DROP TABLE IF EXISTS sestavine CASCADE;")
        cur.execute("DROP TABLE IF EXISTS recepti CASCADE;")
        cur.execute("DROP TABLE IF EXISTS uporabniki CASCADE;")
        cur.execute("DROP TABLE IF EXISTS favourite CASCADE;")
        cur.execute("DROP TABLE IF EXISTS vsecki CASCADE;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Napaka:", e)
    finally:
        cur.close()
        conn.close()


    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/admin/backup_podatki')
def backup_podatki():
    createBackup()

    return redirect(url_for('admin.admin_panel'))
       