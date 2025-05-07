from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from recipe_scrapers import scrape_me
import re

# Initialize Flask app
app = Flask(__name__)

# Configure SQLAlchemy to connect to your PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@db:5432/baza'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Initialize the database
db = SQLAlchemy(app)

# Define a simple User model (this is just an example, adapt it to your needs)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Home route
@app.route('/')
def index():
    return render_template("home.html")



url_pattern = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


@app.route('/scrape', methods=['POST'])
def scrape(url=None):
  url = request.form['url'] if url is None else url

  if not url or not re.match(url_pattern, url):
    return render_template('index.html', message='Invalid URL')

  scraper = scrape_me(url)
  recipe_data = {
      'title': scraper.title(),
      'url': url,
      'ingredients': scraper.ingredients(),
      'instructions': scraper.instructions(),
      'image_url': scraper.image(),
  }

  return render_template('scraper.html')


# Main entry point
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # This will create the tables for your models
    app.run(host="0.0.0.0", port=5000, debug=True)
