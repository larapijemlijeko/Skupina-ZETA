from flask import Flask
from models import app, db, User

@app.route('/')
def index():
    return "PostgreSQL with SQLAlchemy works!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
