from flask import Flask

import controllers.index


f_app = Flask(__name__)

@f_app.get('/')
def home():
    return controllers.index.home()
