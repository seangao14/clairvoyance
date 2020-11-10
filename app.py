from flask import Flask, render_template, url_for, request, redirect, flash
from flask_navigation import Navigation
from clairvoyance.match_history import *
from clairvoyance.game_parser import *
from clairvoyance.prediction import *
from clairvoyance.timeline import *

app = Flask(__name__)
nav = Navigation(app)

nav.Bar('main', [
    nav.Item('Home', 'index'),
    nav.Item('Calculator', 'calculator'),
    nav.Item('Github', 'github')
])

@app.route('/github')
def github():
    return redirect('https://github.com/seangao14/clairvoyance')

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        user = request.form['user']
        return redirect(url_for('match_history', summoner_name = user))
    return render_template('home.html')

@app.route('/matches/<summoner_name>')
def match_history(summoner_name):
    try:
        summoner = get_account_data(summoner_name)
        if summoner == -1:
            return render_template('404.html', name = summoner_name)
        return render_template('match_history.html', summoner = summoner)
    except:
        return 'API key error!'

@app.route('/graph/<match_id>')
def graph(match_id):
    try:
        frames = get_frames(match_id)
        if frames == -1:
            return render_template('404.html', game = match_id)
        game = get_game_data(match_id)
        pred = predict(game)
        gd = list(np.array(get_gd(game))*3 + 0.5)
        xpd = list(np.array(get_xpd(game))*4 + 0.5)
        return render_template('graph.html', match=match_id, frames=frames, pred=pred, gd=gd, xpd=xpd)
    except:
        return 'API key error!'

@app.route('/calculator/<match_id>/<frame_id>', methods=['POST', 'GET'])
def custom_calculator(match_id, frame_id):
    try:
        game = get_game_data(match_id)
    except:
        print (match_id)
        return render_template('404.html', game = match_id)
    frame = game[int(frame_id)]
    data = export_frame(match_id, frame)
    # data = {
    #     'b_air': '0', 
    #     'b_earth': '0', 
    #     'b_fire': '0', 
    #     'b_water': '0',
    #     'r_air': '0', 
    #     'r_earth': '0', 
    #     'r_fire': '0', 
    #     'r_water': '0', 
    #     'b_herald': '0',
    #     'r_herald': '0',
    #     'baron': '2',
    #     'elder': '2'
    # }
    if request.method == 'POST':
        try:
            data = request.form
            champions = [data['b1'], data['b2'], data['b3'], data['b4'], data['b5'],
                        data['r1'], data['r2'], data['r3'], data['r4'], data['r5']]
            
            b_levels = [float(data['b1l']), float(data['b2l']), float(data['b3l']), float(data['b4l']), float(data['b5l']), ]
            r_levels = [float(data['r1l']), float(data['r2l']), float(data['r3l']), float(data['r4l']), float(data['r5l']), ]

            bg = float(data['b_gold'])
            rg = float(data['r_gold'])

            bk = float(data['b_kills'])
            rk = float(data['r_kills'])

            bt = float(data['b_towers'])
            rt = float(data['r_towers'])

            bi = float(data['b_inhibs'])
            ri = float(data['r_inhibs'])

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

            # print(data)
            # print(type(data))

            return render_template('calculator.html', data=data, pred=pred)
        except Exception as e:
            return f'Something went wrong, please go back and check your inputs.\n Error: {e}'
    return render_template('calculator.html', data=data)

@app.route('/calculator', methods=['POST', 'GET'])
def calculator():
    '''
    list of keys:
    b1 - b5        (champion strings)
    b1l - b5l      (champion levels)
    r1 - r5
    r1l - r5l
    b_gold
    r_gold
    b_kills
    r_kills
    b_towers
    r_towers
    b_inhibs
    r_inhibs
    baron
    elder
    b_air/earth/fire/water
    r_air/earth/fire/water
    '''


    data = {
        'b_air': '0', 
        'b_earth': '0', 
        'b_fire': '0', 
        'b_water': '0',
        'r_air': '0', 
        'r_earth': '0', 
        'r_fire': '0', 
        'r_water': '0', 
        'b_herald': '0',
        'r_herald': '0',
        'baron': '2',
        'elder': '2'
    }
    if request.method == 'POST':
        try:
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

            # print(data)
            # print(type(data))

            return render_template('calculator.html', data=data, pred=pred)
        except Exception as e:
            return f'Something went wrong, please go back and check your inputs.\n Error: {e}'
    return render_template('calculator.html', data=data)

# @app.route('/match_history', methods=['POST', 'GET'])
# def match_history():
#     return render_template('match_history.html')

if __name__ == "__main__":
    app.run(debug=True)