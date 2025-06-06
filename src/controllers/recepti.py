from flask import Blueprint, render_template, abort, request
import db
import re
from zoneinfo import ZoneInfo

recepti_bp = Blueprint('recepti', __name__)

@recepti_bp.route('/recepti')
def seznam_receptov():
    oznaka = request.args.get('oznaka')
    
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        if oznaka:
            cur.execute("""
                SELECT r.id, r.naslov, r.opis, r.cas_priprave, r.slika_url
                FROM recepti r
                JOIN oznake o ON r.id = o.recept_id
                WHERE o.oznaka = %s
                ORDER BY r.datum_kreiranja DESC
            """, (oznaka,))
        else:
            cur.execute("""
                SELECT id, naslov, opis, cas_priprave, slika_url
                FROM recepti
                ORDER BY datum_kreiranja DESC
            """)
            
        recepti = cur.fetchall()
        seznam_receptov = []
        for recept in recepti:
            slug = ustvari_slug(recept[1])
            seznam_receptov.append({
                'id': recept[0],
                'naslov': recept[1],
                'opis': recept[2],
                'cas_priprave': recept[3],
                'slika_url': recept[4],
                'slug': slug
            })
        return render_template('recepti.html', recepti=seznam_receptov)
    except Exception as e:
        print("Napaka:", e)
        return render_template('recepti.html', recepti=[])
    finally:
        cur.close()
        conn.close()

@recepti_bp.route('/recepti/<slug>')
def prikazi_recept(slug):
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'recepti'
        """)
        columns = [col[0] for col in cur.fetchall()]
        
        select_fields = ['id', 'naslov', 'opis']
        if 'cas_priprave' in columns:
            select_fields.append('cas_priprave')
        if 'slika_url' in columns:
            select_fields.append('slika_url')
        if 'priprava' in columns:
            select_fields.append('priprava')
        if 'datum_kreiranja' in columns:
            select_fields.append('datum_kreiranja')
        if 'avtor_id' in columns:
            select_fields.append('avtor_id')
        if 'tezavnost' in columns:
            select_fields.append('tezavnost')
            
        query = f"""
            SELECT {', '.join(select_fields)}
            FROM recepti
        """
        
        cur.execute(query)
        recepti = cur.fetchall()
        recept_data = None
        
        column_index = {field: i for i, field in enumerate(select_fields)}
        
        for recept in recepti:
            recept_slug = ustvari_slug(recept[column_index['naslov']])
            if recept_slug == slug:
                recept_data = {
                    'id': recept[column_index['id']],
                    'naslov': recept[column_index['naslov']],
                    'opis': recept[column_index['opis']],
                }

                if 'cas_priprave' in column_index:
                    recept_data['cas_priprave'] = recept[column_index['cas_priprave']]
                if 'slika_url' in column_index:
                    recept_data['slika_url'] = recept[column_index['slika_url']]
                if 'priprava' in column_index:
                    recept_data['priprava'] = recept[column_index['priprava']]
                if 'datum_kreiranja' in column_index:
                    datum_kreiranja = recept[column_index['datum_kreiranja']]
                    if datum_kreiranja:
                        if datum_kreiranja.tzinfo is None:
                            datum_kreiranja = datum_kreiranja.replace(tzinfo=ZoneInfo("UTC"))
                        recept_data['datum_kreiranja'] = datum_kreiranja.astimezone(ZoneInfo("Europe/Ljubljana"))
                    else:
                        recept_data['datum_kreiranja'] = None
                if 'avtor_id' in column_index and recept[column_index['avtor_id']]:
                    avtor_id = recept[column_index['avtor_id']]
                    cur.execute("SELECT ime FROM uporabniki WHERE id = %s", (avtor_id,))
                    uporabnik = cur.fetchone()
                    recept_data['avtor'] = uporabnik[0] if uporabnik else None
                else:
                    recept_data['avtor'] = None
                if 'tezavnost' in column_index:
                    recept_data['tezavnost'] = recept[column_index['tezavnost']]
                else:
                    recept_data['tezavnost'] = None

                cur.execute("""
                    SELECT ime, kolicina, enota, st_oseb
                    FROM sestavine
                    WHERE recept_id = %s
                """, (recept_data['id'],))
                sestavine = cur.fetchall()

                def format_kolicina(kolicina):
                    try:
                        return float(kolicina)
                    except:
                        return 0.0

                surovine = []
                for ime, kolicina, enota, st_oseb in sestavine:
                    surovina = {
                        'ime': ime,
                        'kolicina': format_kolicina(kolicina),
                        'enota': enota,
                        'st_oseb': st_oseb or 1
                    }
                    surovine.append(surovina)

                recept_data['surovine'] = surovine
                recept_data['st_oseb'] = surovine[0]['st_oseb'] if surovine else 1

                cur.execute("""
                    SELECT oznaka
                    FROM oznake
                    WHERE recept_id = %s
                """, (recept_data['id'],))
                oznake = cur.fetchall()
                recept_data['oznake'] = [oznaka[0] for oznaka in oznake]

                break
        
        if recept_data:
            return render_template('recept-podrobno.html', recept=recept_data)
        else:
            abort(404)
    except Exception as e:
        print("Napaka pri prikazu recepta:", e)
        abort(500)
    finally:
        cur.close()
        conn.close()

def ustvari_slug(naslov):
    if not naslov:
        return "recept"
        
    slug = naslov.lower()
    slug = slug.replace('č', 'c').replace('š', 's').replace('ž', 'z').replace('ć', 'c').replace('đ', 'd')
    slug = re.sub(r'[^a-z0-9\s]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = slug.strip('-')
    return slug if slug else "recept"

@recepti_bp.route('/dodaj-komentar', methods=['POST'])
def dodaj_komentar():
    data = request.get_json()
    recept_id = data.get('recept_id')
    komentar = data.get('komentar')
    avtor = data.get('avtor', 'Anonimno')  # Uporabite avtor iz forme

    if not recept_id or not komentar:
        return jsonify({'status': 'error', 'message': 'Manjkajoči podatki.'}), 400

    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO komentarji (recept_id, avtor, komentar)
            VALUES (%s, %s, %s)
        """, (recept_id, avtor, komentar))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Napaka pri dodajanju komentarja:", e)
        return jsonify({'status': 'error'}), 500
    finally:
        cur.close()
        conn.close()

@recepti_bp.route('/komentarji/<int:recept_id>')
def komentarji_za_recept(recept_id):
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT avtor, komentar, 
                   TO_CHAR(datum AT TIME ZONE 'UTC' AT TIME ZONE 'Europe/Ljubljana', 'DD.MM.YYYY HH24:MI') as formatted_datum
            FROM komentarji
            WHERE recept_id = %s
            ORDER BY datum DESC
        """, (recept_id,))
        komentarji = cur.fetchall()
        return jsonify([{
            'avtor': k[0], 
            'komentar': k[1], 
            'datum': k[2]
        } for k in komentarji])
    except Exception as e:
        print("Napaka pri branju komentarjev:", e)
        return jsonify([])
    finally:
        cur.close()
        conn.close()
