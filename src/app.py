from flask import Flask

import controllers.index
import controllers.prijava
import controllers.recepti
import controllers.registracija


f_app = Flask(__name__)

@f_app.get('/')
def home():
    return controllers.index.home()

@f_app.get('/recepti')
def recepti():
    return controllers.recepti.recepti()

@f_app.route('/prijava')
def prijava():
    return controllers.prijava.prijava()

@f_app.route('/registracija')
def registracija():
    return controllers.registracija.registracija()