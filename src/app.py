from flask import Flask, render_template, request, redirect, url_for, session
from recipe_scrapers import scrape_me

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


f_app = Flask(__name__)


@f_app.get('/')
def home():
    return controllers.index.home()

@f_app.get('/recepti')
def recepti():
    return controllers.recepti.recepti()

@f_app.get('/oddajrecept')
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

@f_app.route('/prijava')
def prijava():
    return controllers.prijava.prijava()

@f_app.route('/registracija')
def registracija():
    return controllers.registracija.registracija()

@f_app.route('/pozabljenogeslo')
def pozabljenogeslo():
    return controllers.pozabljenogeslo.pozabljenogeslo()

@f_app.route('/scraper', methods=['GET', 'POST'])
def scrape():
    if request.method == 'POST':
        url = request.form['url']
        scraper = scrape_me(url)
        recipe_data = {
            'title': scraper.title(),
            'url': url,
            'ingredients': scraper.ingredients(),
            'instructions': scraper.instructions(),
            'image_url': scraper.image(),
        }
    else:
        recipe_data = None

    return render_template('scraper.html', recipe=recipe_data)

@f_app.route("/nagradneigre", methods=["GET", "POST"])
def nagradneigre():
    return controllers.nagradneigre.nagradne_igre()

if __name__ == "__main__":
    f_app.run(port=5000, debug=True)

#