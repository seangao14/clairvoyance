from flask import Flask, render_template, url_for, request, redirect, flash
from flask_navigation import Navigation
from clairvoyance.match_history import *

app = Flask(__name__)
nav = Navigation(app)

nav.Bar('main', [
    nav.Item('home', 'index'),
    nav.Item('calculator', 'calculator')
])

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        print("hello")
        user = request.form['user']
        return redirect(url_for('match_history', summoner_name = user))
    return render_template('home.html')

@app.route('/matches/<summoner_name>')
def match_history(summoner_name):
    summoner = get_account_data(summoner_name)
    if summoner == -1:
        return render_template('404.html', name = summoner_name)
    return render_template('match_history.html', summoner = summoner)

@app.route('/calculator', methods=['POST', 'GET'])
def calculator():
    return render_template('calculator.html')

# @app.route('/match_history', methods=['POST', 'GET'])
# def match_history():
#     return render_template('match_history.html')

if __name__ == "__main__":
    app.run(debug=True)