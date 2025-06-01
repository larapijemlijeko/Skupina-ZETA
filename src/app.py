from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from recipe_scrapers import scrape_me
from controllers.admin import admin_bp
from controllers.recepti import recepti_bp
import db

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
from models.zaBazo import create_tables
from models.dbBackup import initializeScheduler
from controllers import svetovna_kuhinja



f_app = Flask(__name__)
f_app.secret_key = "dev"  # Add a secret key if sessions are used

f_app.register_blueprint(admin_bp)
f_app.secret_key = "mojaTajnaVrednost123"  
f_app.register_blueprint(recepti_bp)

create_tables()

initializeScheduler()

@f_app.get('/')
def home():
    return controllers.index.home()

@f_app.get('/recepti')
def recepti():
    return redirect(url_for('recepti.seznam_receptov'))

@f_app.route('/oddajrecept', methods=['GET', 'POST'])
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

@f_app.route('/prijava')
def prijava():
    return controllers.prijava.prijava()

@f_app.route('/registracija')
def registracija():
    return controllers.registracija.registracija()

@f_app.route('/pozabljenogeslo')
def pozabljenogeslo():
    return controllers.pozabljenogeslo.pozabljenogeslo()

@f_app.route("/nagradneigre", methods=["GET", "POST"])
def nagradneigre():
    return controllers.nagradneigre.nagradne_igre()

@f_app.route('/scraper', methods=['GET', 'POST'])
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


@f_app.route('/add_favorites', methods=['POST'])
def favorite_scraped():
    data = request.get_json()
    recipe = data.get('recipe')

    if not recipe or 'title' not in recipe or 'url' not in recipe:
        return jsonify({'status': 'error', 'message': 'Invalid recipe data'}), 400

    uporabnik_id = 1  # FIXED user ID, ker še nimaš login sistema

    conn = db.get_connection()
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
        conn.close()

@f_app.route('/scraped')
def view_scraped():
    uporabnik_id = 1  # FIXED user ID

    conn = db.get_connection()
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
        conn.close()

    return render_template('scraped.html', recipes=scraped_recipes)

@f_app.route('/report', methods=['GET','POST'])
def report():

    submitted = False

    if request.method == 'POST':
       tip_problema = request.form['problemType']
       opis = request.form['description']

       conn = None
       try:
           conn =  db.get_connection()
           cur = conn.cursor()
           cur.execute("""
                INSERT INTO napake (tip_problema, opis)
                VALUES (%s, %s)       
            """, (tip_problema, opis))
           
           conn.commit()
           cur.close()
           conn.close()
           submitted = True

           # lets go back to home page if everything is ok
           return redirect(url_for('home'))
           
       except Exception as e:
           print(f"Error in /report: {e}")
           return "There was an error processing your report.", 500
       finally:
           if conn:
               conn.close()
           else:
               submitted = False
    elif request.method == 'POST':  
        return render_template('prijavi-napaka.html')       
    return render_template('prijavi-napaka.html', submitted=submitted) 


if __name__ == "__main__":
    f_app.run(port=5000, debug=True)