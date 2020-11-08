from flask import Flask, render_template, url_for, request, redirect, flash
from flask_navigation import Navigation
from clairvoyance.match_history import *
from clairvoyance.game_parser import *
from clairvoyance.prediction import *

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
    if request.method == 'POST':
        data = request.form
        champions = [data['b1'], data['b2'], data['b3'], data['b4'], data['b5'],
                     data['r1'], data['r2'], data['r3'], data['r4'], data['r5']]
        
        b_levels = [int(data['b1l']), int(data['b2l']), int(data['b3l']), int(data['b4l']), int(data['b5l']), ]
        r_levels = [int(data['r1l']), int(data['r2l']), int(data['r3l']), int(data['r4l']), int(data['r5l']), ]

        bg = int(data['b_gold'])
        rg = int(data['r_gold'])

        bk = int(data['b_kills'])
        rk = int(data['r_kills'])

        bt = int(data['b_towers'])
        rt = int(data['r_towers'])

        bi = int(data['b_inhibs'])
        ri = int(data['r_inhibs'])

        # for elder and baron:
        # 0 = blue, 1 = red, 2 = neither
        b_baron = 1 if int(data['baron']) == 0 else 0
        r_baron = 1 if int(data['baron']) == 1 else 0

        b_elder = 1 if int(data['elder']) == 0 else 0
        r_elder = 1 if int(data['elder']) == 1 else 0

        bm = [int(data['b_air']), int(data['b_earth']), int(data['b_fire']), int(data['b_water']), 
                b_elder, int(data['b_herald']), b_baron]
        
        rm = [int(data['r_air']), int(data['r_earth']), int(data['r_fire']), int(data['r_water']), 
                r_elder, int(data['r_herald']), r_baron]
        
        game = custom_game(timestamp=0.5, champions=champions, 
            blue_gold=bg, red_gold=rg, blue_levels=b_levels, red_levels=r_levels,
            bk=bk, rk=rk, bt=bt, rt=rt, bi=bi, ri=ri, bm=bm, rm=rm)
        # print(game)
        # print(len(game))
        pred = predict(game)

        print(data)
        print(type(data))

        return render_template('calculator.html', data=data, pred=pred)
    return render_template('calculator.html')

# @app.route('/match_history', methods=['POST', 'GET'])
# def match_history():
#     return render_template('match_history.html')

if __name__ == "__main__":
    app.run(debug=True)