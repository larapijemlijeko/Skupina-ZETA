from flask import Blueprint, request, jsonify
from db import get_connection

kalorije_bp = Blueprint("kalorije", __name__)

@kalorije_bp.route('/shrani_kalorije', methods=['POST'])
def shrani_kalorije():
    data = request.get_json()

    spol = data.get('spol')
    starost = data.get('starost')
    visina = data.get('visina')
    teza = data.get('teza')
    aktivnost = data.get('aktivnost')
    kalorije_vzdrz = data.get('kalorije_vzdrzevanje')
    kalorije_hujs = data.get('kalorije_hujsanje')

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO uporabniki_podatki (
                visina, teza, starost, spol, aktivnost,
                kalorije_za_vzdrzevanje, kalorije_za_hujsanje
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (visina, teza, starost, spol, aktivnost, kalorije_vzdrz, kalorije_hujs))
        conn.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        print("Napaka pri shranjevanju kalorij:", e)
        return jsonify({'status': 'error'}), 500
    finally:
        cur.close()
        conn.close()