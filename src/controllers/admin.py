from flask import Blueprint, render_template, redirect, url_for
import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def admin_panel():
    return render_template('admin.html')

@admin_bp.route('/admin/dodaj')
def dodaj_testne_podatke():
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO uporabniki (uporabnisko_ime, email, geslo)
            VALUES ('adminuser', 'admin@example.com', 'admin123')
            RETURNING id;
        """)
        uporabnik_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO recepti (naslov, opis, priprava, cas_priprave, tezavnost, slika_url, uporabnik_id)
            VALUES ('Admin recept', 'Opis', 'Priprava', 20, 1, '', %s)
            RETURNING id;
        """, (uporabnik_id,))
        recept_id = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO sestavine (recept_id, ime, kolicina, enota)
            VALUES (%s, 'Sol', '1', 'žlička');
        """, (recept_id,))

        cur.execute("""
            INSERT INTO oznake (recept_id, oznaka)
            VALUES (%s, 'Testna');
        """, (recept_id,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Napaka:", e)
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
