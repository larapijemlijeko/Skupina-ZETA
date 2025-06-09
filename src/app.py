from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from flask_login import LoginManager, login_required, current_user
from recipe_scrapers import scrape_me
import os
from datetime import timedelta
import random

# Import existing controllers
from controllers.admin import admin_bp
from controllers.recepti import recepti_bp
from controllers.kalorije import kalorije_bp
import controllers.index
import controllers.prijava
import controllers.recepti
import controllers.oddajrecept
import controllers.novice
import controllers.kontakt
import controllers.vprasanja
import controllers.registracija
import controllers.pozabljenogeslo
import controllers.nagradneigre
import controllers.anketa
import controllers.nakljucniRecepti
import controllers.kviz
import controllers.forum
from controllers.forum import forum_bp
from controllers import svetovna_kuhinja
from controllers.admin_questions import admin_questions_bp

# Import user management modules
from models.uporabniki import User
from controllers.auth_controller import auth_bp

# Import database and utility modules
import db
from models import recepti
from models.zaBazo import create_tables
from models.dbBackup import initializeScheduler

f_app = Flask(__name__)

# Configuration
f_app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mojaTajnaVrednost123')
f_app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Inicializacija Flask-Login
login_manager = LoginManager()
login_manager.init_app(f_app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Za dostop do te strani se morate prijaviti.'
login_manager.login_message_category = 'info'

# Blueprint registracija
f_app.register_blueprint(admin_bp)
f_app.register_blueprint(recepti_bp)
f_app.register_blueprint(kalorije_bp)
f_app.register_blueprint(auth_bp)  # Add user authentication
f_app.register_blueprint(forum_bp)
f_app.register_blueprint(admin_questions_bp)

# Initialize database and scheduler
create_tables()
initializeScheduler()

# Flask-Login uporabniški nalagalnik
@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    conn = db.get_connection()
    user = User.get(conn, user_id)
    conn.close()
    return user

# DB povezava za vsako prošnjo
@f_app.before_request
def before_request():
    g.db = db.get_connection()

@f_app.teardown_request
def teardown_request(exception):
    db_conn = getattr(g, 'db', None)
    if db_conn is not None:
        db_conn.close()

@f_app.context_processor
def inject_user():
    """Inject current user into templates"""
    return dict(current_user=current_user)

# Main routes
@f_app.get('/')
def home():
    return controllers.index.home()

# SPREMENJENA RUTA ZA RECEPTI - zdaj podpira filter po oznaki (sezoni)
@f_app.route('/recepti')
def recepti():
    oznaka = request.args.get('oznaka', None)
    return controllers.recepti.seznam_receptov(oznaka)

@f_app.route('/oddajrecept', methods=['GET', 'POST'])
@login_required  # potrebna prijava
def oddajrecept():
    return controllers.oddajrecept.oddajrecept()

@f_app.route('/novice')
def novice():
    return controllers.novice.novice()

@f_app.route('/kontakt')
def kontakt():
    return controllers.kontakt.kontakt()
    
@f_app.route('/vprasanja')
def vprasanja():
    return controllers.vprasanja.vprasanja()

@f_app.route('/anketa')
def anketa():
    return controllers.anketa.anketa()

# Naslednje rute so komentirane ker se uporabljajo novi auth blueprinti
# @f_app.route('/prijava')
# def prijava():
#     return controllers.prijava.prijava()

# @f_app.route('/registracija')
# def registracija():
#     return controllers.registracija.registracija()

# @f_app.route('/pozabljenogeslo')
# def pozabljenogeslo():
#     return controllers.pozabljenogeslo.pozabljenogeslo()

@f_app.route("/nagradneigre", methods=["GET", "POST"])
def nagradneigre():
    return controllers.nagradneigre.nagradne_igre()

@f_app.route('/scraper', methods=['GET', 'POST'])
@login_required  # Add login requirement
def scrape():
    recipe_data = None
    error = None

    if request.method == 'POST':
        try:
            url = request.form['url']
            scraper = scrape_me(url)

            title = scraper.title()
            ingredients = scraper.ingredients()
            instructions = scraper.instructions()
            image_url = scraper.image()

            if not title:
                raise ValueError("Recipe title could not be extracted.")

            recipe_data = {
                'title': title,
                'url': url,
                'ingredients': ingredients,
                'instructions': instructions,
                'image_url': image_url
            }
        except Exception as e:
            error = f"Failed to scrape the recipe: {str(e)}"

    return render_template('scraper.html', recipe=recipe_data, error=error)

@f_app.route("/svetovnakuhinjamapa")
def svetovnakuhinjamapa():
    return render_template("svetovnakuhinjamapa.html")

@f_app.route("/recepti/regija/<ime_regije>")
def recepti_po_regiji(ime_regije):
    return svetovna_kuhinja.recepti_po_regiji(ime_regije)

@f_app.route('/nakljucen-recept')
def nakljucen_recept():
    conn = g.db
    cur = conn.cursor()

    cur.execute("SELECT id FROM recepti")
    ids = [row[0] for row in cur.fetchall()]
    
    if not ids:
        return "Ni receptov."

    nakljucni_id = random.choice(ids)

    cur.execute("SELECT * FROM recepti WHERE id = %s", (nakljucni_id,))
    recept = cur.fetchone()

    cur.execute("SELECT * FROM sestavine WHERE recept_id = %s", (nakljucni_id,))
    surovine = cur.fetchall()

    recept_dict = {
        "id": recept[0],
        "naslov": recept[1],
        "opis": recept[2],
        "priprava": recept[3],
        "cas_priprave": recept[4],
        "tezavnost": recept[5],
        "slika_url": recept[6],
        "datum_kreiranja": recept[8],
        "surovine": [
            {
                "ime": s[2],
                "kolicina": s[3],
                "enota": s[4],
                "st_oseb": s[5]
            } for s in surovine
        ]
    }

    cur.close()
    return render_template("nakljucni-podrobno.html", recept=recept_dict)

@f_app.route('/add_favorites', methods=['POST'])
@login_required  # Add login requirement
def favorite_scraped():
    data = request.get_json()
    recipe = data.get('recipe')

    if not recipe or 'title' not in recipe or 'url' not in recipe:
        return jsonify({'status': 'error', 'message': 'Invalid recipe data'}), 400

    # Use current authenticated user instead of fixed ID
    uporabnik_id = current_user.id

    conn = g.db
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO scraped (uporabnik_id, naslov, url)
            VALUES (%s, %s, %s)
            ON CONFLICT (uporabnik_id, url) DO NOTHING;
        """, (
            uporabnik_id,
            recipe['title'],
            recipe['url']
        ))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Scraped recipe saved!'})
    except Exception as e:
        conn.rollback()
        print("DB Error:", e)
        return jsonify({'status': 'error', 'message': 'Failed to save recipe.'}), 500
    finally:
        cur.close()

@f_app.route('/scraped')
@login_required  # Add login requirement
def view_scraped():
    # Use current authenticated user instead of fixed ID
    uporabnik_id = current_user.id

    conn = g.db
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT naslov, url, datum_shranjevanja
            FROM scraped
            WHERE uporabnik_id = %s
            ORDER BY datum_shranjevanja DESC
        """, (uporabnik_id,))
        scraped_recipes = cur.fetchall()
    except Exception as e:
        print("DB Error:", e)
        scraped_recipes = []
    finally:
        cur.close()

    return render_template('scraped.html', recipes=scraped_recipes)

@f_app.route('/report', methods=['GET','POST'])
def report():

    submitted = False

    if request.method == 'POST':
       tip_problema = request.form['problemType']
       opis = request.form['description']

       conn = None
       try:
           conn = g.db
           cur = conn.cursor()
           cur.execute("""
                INSERT INTO napake (tip_problema, opis)
                VALUES (%s, %s)       
            """, (tip_problema, opis))
           
           conn.commit()
           cur.close()
           submitted = True

           # lets go back to home page if everything is ok
           return redirect(url_for('home'))
           
       except Exception as e:
           print(f"Error in /report: {e}")
           return "There was an error processing your report.", 500
       finally:
           if conn:
               pass  # Connection will be closed by teardown_request
           else:
               submitted = False
    elif request.method == 'POST':  
        return render_template('prijavi-napaka.html')       
    return render_template('prijavi-napaka.html', submitted=submitted)

@f_app.route('/kviz')
def kviz_api():
    return controllers.kviz.get_kviz_questions()

@f_app.route('/profil')
@login_required
def profile():
    """User profile with liked recipes"""
    from models.vsecki import LikeSystem
    
    conn = g.db
    
    # Všečkani recepti
    liked_recipes = LikeSystem.get_user_liked_recipes(conn, current_user.id)
    
    # Tvoji recepti
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, COUNT(v.id) as like_count
        FROM recepti r
        LEFT JOIN vsecki v ON r.id = v.recept_id
        WHERE r.uporabnik_id = %s
        GROUP BY r.id
        ORDER BY r.datum_kreiranja DESC
    """, (current_user.id,))
    
    my_recipes = cur.fetchall()
    cur.close()
    
    return render_template('profile.html', 
                         liked_recipes=liked_recipes,
                         my_recipes=my_recipes)

# Error handlers
@f_app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
@f_app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@f_app.route("/iskalnik")
def iskalnik():
    return render_template("iskalnik.html")

@f_app.route("/api/recipes")
def api_recipes():
    title = request.args.get("title", "")
    conn = db.get_connection()
    cur = conn.cursor()
    try:
        if len(title) > 0:
            cur.execute("""
                SELECT id, naslov, opis, cas_priprave, slika_url
                FROM recepti
                WHERE naslov ILIKE %s
            """, (f"%{title}%",))
        else:
            cur.execute("""
                SELECT id, naslov, opis, cas_priprave, slika_url
                FROM recepti
               WHERE id >= 0""")
          
        rows = cur.fetchall()
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "naslov": row[1],
                "opis": row[2],
                "cas_priprave": row[3],
                "slika_url": row[4]
            })
        return jsonify(results)
    except Exception as e:
        print("Napaka pri iskanju:", e)
        return jsonify([]), 500
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    f_app.run(port=5000, debug=True)