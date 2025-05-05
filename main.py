from flask import Flask
app = Flask(__name__)
@app.get('/')
def hello():
 return 'Hello, D-Flask!'
if __name__ == '__main__':
 app.run(host='0.0.0.0')

