from flask import Flask, render_template, url_for, request, redirect
from flask_navigation import Navigation

app = Flask(__name__)
nav = Navigation(app)

nav.Bar('main', [
    nav.Item('Home', 'index'),
    nav.Item('Calculator', 'calculator'),
])

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('home.html')

@app.route('/calculator', methods=['POST', 'GET'])
def calculator():
    return render_template('calculator.html')

if __name__ == "__main__":
    app.run(debug=True)