from flask import jsonify
import db

def recepti_po_regiji(ime_regije):
    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT r.id, r.naslov, r.opis, r.drzava
        FROM recepti r
        JOIN recepti_regije rr ON r.id = rr.recept_id
        JOIN regije g ON rr.regija_id = g.id
        WHERE g.ime = %s
    """, (ime_regije,))
    
    recepti = cur.fetchall()
    conn.close()

    return jsonify([{"id": r[0], "naslov": r[1], "opis": r[2], "drzava": r[3]} for r in recepti])

def recepti_po_drzavi(ime_drzave):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, naslov, opis, drzava
        FROM recepti
        WHERE drzava = %s
    """, (ime_drzave,))
    recepti = cur.fetchall()
    conn.close()

    return jsonify([{"id": r[0], "naslov": r[1], "opis": r[2], "drzava": r[3]} for r in recepti])


