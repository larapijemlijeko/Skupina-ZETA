from flask import Flask

import controllers.index
import controllers.prijava
import controllers.recepti
import controllers.novice
import controllers.vprasanja
import controllers.registracija
import controllers.pozabljenogeslo


f_app = Flask(__name__)

@f_app.get('/')
def home():
    return controllers.index.home()

@f_app.get('/recepti')
def recepti():
    return controllers.recepti.recepti()

@f_app.route('/novice')
def novice():
    return controllers.novice.novice()
    
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