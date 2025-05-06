from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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

# Main entry point
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # This will create the tables for your models
    app.run(host="0.0.0.0", port=5000, debug=True)
    