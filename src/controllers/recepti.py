from flask import Blueprint, render_template, abort
import db
import re
from zoneinfo import ZoneInfo


recepti_bp = Blueprint('recepti', __name__)

@recepti_bp.route('/recepti')
def seznam_receptov():
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, naslov, opis, cas_priprave, slika_url
            FROM recepti
            ORDER BY datum_kreiranja DESC
        """)
        recepti = cur.fetchall()
        seznam_receptov = []
        for recept in recepti:
            # Ustvarimo slug za url iz naslova
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
        # Preveri, kateri stolpci obstajajo v tabeli recepti
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'recepti'
        """)
        columns = [col[0] for col in cur.fetchall()]
        
        # Stolpci, ki jih želimo pridobiti
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
            
        # Sestavimo poizvedbo
        query = f"""
            SELECT {', '.join(select_fields)}
            FROM recepti
        """
        
        cur.execute(query)
        recepti = cur.fetchall()
        recept_data = None
        
        # Indeks stolpcev za lažje indeksiranje po tuple
        column_index = {field: i for i, field in enumerate(select_fields)}
        
        for recept in recepti:
            recept_slug = ustvari_slug(recept[column_index['naslov']])
            if recept_slug == slug:
                # Osnovni podatki
                recept_data = {
                    'id': recept[column_index['id']],
                    'naslov': recept[column_index['naslov']],
                    'opis': recept[column_index['opis']],
                }

                # Opcijski podatki, če obstajajo
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

                # Pridobi sestavine
                cur.execute("""
                    SELECT ime, kolicina, enota, st_oseb
                    FROM sestavine
                    WHERE recept_id = %s
                """, (recept_data['id'],))
                sestavine = cur.fetchall()
                # Shranimo število oseb (če obstaja vsaj ena sestavina z navedenim številom oseb)
                if sestavine and sestavine[0][3] is not None:
                    recept_data['st_oseb'] = sestavine[0][3]
                else:
                    recept_data['st_oseb'] = None
                recept_data['sestavine'] = [f"{kolicina} {enota} {ime}" for ime, kolicina, enota, _ in sestavine]


                # Pridobi oznake
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
    """Ustvari URL-friendly slug iz naslova recepta"""
    if not naslov:
        return "recept"
        
    slug = naslov.lower()
    slug = slug.replace('č', 'c').replace('š', 's').replace('ž', 'z').replace('ć', 'c').replace('đ', 'd')
    slug = re.sub(r'[^a-z0-9\s]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = slug.strip('-')
    return slug if slug else "recept"