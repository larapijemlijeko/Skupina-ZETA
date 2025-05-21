from flask import Blueprint, render_template, abort
import db
import re

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
        # Najprej preverimo strukturo tabele recepti
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'recepti'
        """)
        columns = [col[0] for col in cur.fetchall()]
        
        # Gradimo poizvedbo dinamično glede na obstoječe stolpce
        select_fields = ['id', 'naslov', 'opis']
        if 'cas_priprave' in columns:
            select_fields.append('cas_priprave')
        if 'slika_url' in columns:
            select_fields.append('slika_url')
        if 'sestavine' in columns:
            select_fields.append('sestavine')
        if 'postopek' in columns:
            select_fields.append('postopek')
        if 'datum_kreiranja' in columns:
            select_fields.append('datum_kreiranja')
        if 'avtor_id' in columns:
            select_fields.append('avtor_id')
            
        # Sestavimo poizvedbo
        query = f"""
            SELECT {', '.join(select_fields)}
            FROM recepti
        """
        
        cur.execute(query)
        recepti = cur.fetchall()
        recept_data = None
        
        # Ustvarimo slovar za lažji dostop do stolpcev
        column_index = {field: i for i, field in enumerate(select_fields)}
        
        for recept in recepti:
            recept_slug = ustvari_slug(recept[column_index['naslov']])
            if recept_slug == slug:
                recept_data = {
                    'id': recept[column_index['id']],
                    'naslov': recept[column_index['naslov']],
                    'opis': recept[column_index['opis']],
                }
                
                # Dodaj ostale podatke, če so na voljo
                if 'cas_priprave' in column_index:
                    recept_data['cas_priprave'] = recept[column_index['cas_priprave']]
                if 'slika_url' in column_index:
                    recept_data['slika_url'] = recept[column_index['slika_url']]
                
                # Obdelamo sestavine, če so na voljo
                if 'sestavine' in column_index and recept[column_index['sestavine']]:
                    try:
                        import json
                        sestavine = json.loads(recept[column_index['sestavine']])
                        recept_data['sestavine'] = sestavine
                    except json.JSONDecodeError:
                        # Če ni veljaven JSON, razdeli po vrsticah
                        recept_data['sestavine'] = recept[column_index['sestavine']].split('\n')
                    except Exception:
                        recept_data['sestavine'] = []
                else:
                    recept_data['sestavine'] = []
                
                # Dodaj postopek, če je na voljo
                if 'postopek' in column_index:
                    recept_data['postopek'] = recept[column_index['postopek']]
                
                # Dodaj datum, če je na voljo
                if 'datum_kreiranja' in column_index:
                    recept_data['datum_kreiranja'] = recept[column_index['datum_kreiranja']]
                
                # Pridobi avtor ime, če imamo avtor_id
                if 'avtor_id' in column_index and recept[column_index['avtor_id']]:
                    try:
                        avtor_id = recept[column_index['avtor_id']]
                        cur.execute("SELECT ime FROM uporabniki WHERE id = %s", (avtor_id,))
                        uporabnik = cur.fetchone()
                        recept_data['avtor'] = uporabnik[0] if uporabnik else None
                    except Exception as e:
                        print("Napaka pri pridobivanju avtorja:", e)
                        recept_data['avtor'] = None
                else:
                    recept_data['avtor'] = None
                
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
        
    # Pretvorimo v male črke
    slug = naslov.lower()
    # Odstranimo šumnike
    slug = slug.replace('č', 'c').replace('š', 's').replace('ž', 'z').replace('ć', 'c').replace('đ', 'd')
    # Odstranimo vse znake razen črk, številk in presledkov
    slug = re.sub(r'[^a-z0-9\s]', '', slug)
    # Zamenjamo presledke z vezaji
    slug = re.sub(r'\s+', '-', slug)
    # Odstranimo vezaje na začetku in koncu
    slug = slug.strip('-')
    # Če je slug prazen, vrnemo privzeto vrednost
    return slug if slug else "recept"