from flask import Flask, request
from connect import connect
import psycopg2.extras
import os
from auth import auth
import json
import datetime
from flask_cors import CORS
from auth import protected

os.environ['SECRET_KEY'] = 'hello'

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000',
                   'http://localhost:3001', 'https://lying-wordle.netlify.app/'])
app.register_blueprint(auth)


def date_converter(date):
    if isinstance(date, datetime.datetime):
        return date.__str__()


@app.route('/api/v1/games', methods=['GET', 'POST'])
def games():
    if request.method == 'GET':
        conn = connect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        args = request.args.to_dict()
        sql = """SELECT * FROM games"""
        if 'user' in args:
            sql += """ JOIN scores on games.game_id = scores.game_id
                        JOIN users on users.user_id = scores.user_id 
                        WHERE users.user_id = %s"""

        cur.execute(sql, (args.get('user'),))
        print(args.get('user'))
        print(sql)
        games = cur.fetchall()
        result = {'count': len(games), 'games': []}
        for game in games:
            if not game['game_id'] in result['games']:
                result['games'].append(
                    {'id': game['game_id'],
                     'word': game['word'],
                     'lie_rate': game['lie_rate']
                     })

        return result
    else:
        conn = connect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        info = request.get_json()
        word = info.get('word')
        lie_rate = info.get('lie_rate')

        check_duplicate = 'SELECT * FROM games WHERE word = %s AND lie_rate = %s'

        cur.execute(check_duplicate, (word, lie_rate))
        game = cur.fetchone()

        if game == None:
            sql = 'INSERT INTO games (word, lie_rate) VALUES (%s, %s) RETURNING game_id'

            cur.execute(sql, (word, lie_rate))
            game_id = cur.fetchone()['game_id']
            cur.close()
            conn.commit()

            return {'msg': 'Game added successfully', 'game_id': game_id}, 200
        else:
            return {'msg': 'Game already exists', 'game_id': game['game_id']}, 400


@app.route('/api/v1/users', methods=['GET'])
def users():
    if request.method == 'GET':
        conn = connect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute('SELECT * FROM users')
        result = cur.fetchall()
        return result


@app.route('/api/v1/scores', methods=['GET', 'POST'])
@protected  # we don't want people to see scores for games that they have not played yet
def scores(user_id):
    if request.method == 'GET':
        conn = connect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        print(user_id)
        args = request.args.to_dict()
        # Returns all scores, but only for games that the user has played.
        sql = """SELECT * FROM scores
                JOIN games on games.game_id = scores.game_id
                JOIN users on users.user_id = scores.user_id
                WHERE scores.game_id = ANY(
                    SELECT (games.game_id) FROM games 
                    JOIN scores ON games.game_id = scores.game_id
                    WHERE scores.user_id = %s)
                """
        query_vars = (user_id,)
        # Add filters if there are query params
        if 'user' in args and 'game' in args:
            sql += ' AND users.user_id = %s AND games.game_id = %s'
            query_vars += (args.get('user'), args.get('game'))
        elif 'user' in args:
            sql += ' AND users.user_id = %s'
            query_vars += (args.get('user'),)
        elif 'game' in args:
            sql += ' AND games.game_id = %s'
            query_vars += (args.get('game'),)

        cur.execute(sql, query_vars)
        scores = cur.fetchall()
        result = {'count': len(scores), 'scores': []}
        print(scores)
        if len(scores) == 0:
            return result
        if 'user' in args:
            result['user'] = {
                'id': scores[0]['user_id'],
                'name': scores[0]['name'],
                'username': scores[0]['username']
            }
        if 'game' in args:
            result['game'] = {
                'word': scores[0]['word'],
                'lie_rate': scores[0]['lie_rate']
            }
        for score in scores:
            if 'user' in args and 'game' in args:
                result['scores'].append({
                    'score': score['score'],
                    'time': score['time']
                })
            elif 'user' in args:
                result['scores'].append({
                    'score': score['score'],
                    'time': score['time'],
                    'game': {
                        'word': score['word'],
                        'lie_rate': score['lie_rate']
                    }
                })
            elif 'game' in args:
                result['scores'].append({
                    'user': {
                        'id': score['user_id'],
                        'name': score['name'],
                        'username': score['username']
                    },
                    'score': score['score'],
                    'time': score['time'],
                })
            else:
                result['scores'].append({
                    'user': {
                        'id': score['user_id'],
                        'name': score['name'],
                        'username': score['username']
                    },
                    'score': score['score'],
                    'time': score['time'],
                    'game': {
                        'word': score['word'],
                        'lie_rate': score['lie_rate']
                    }
                })
        return result
    else:
        conn = connect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        info = request.get_json()
        game_id = info.get('game_id')
        score = info.get('score')
        time = info.get('time')
        guesses = info.get('guesses')

        # Check to make sure the player has not played this game already
        check_sql = 'SELECT COUNT(*) FROM scores WHERE game_id = %s AND user_id = %s'
        try:
            cur.execute(check_sql, (game_id, user_id))
            games = cur.fetchall()[0]['count']
            if games > 0:
                return {'msg': 'You have already played this game.'}, 200
        except:
            return {'msg': 'Unexpected error occurred.'}, 500

        sql = 'INSERT INTO scores (user_id, game_id, score, time, guesses) VALUES (%s, %s, %s, %s, %s)'

        try:
            cur.execute(sql, (user_id, game_id, score, time, guesses))
            cur.close()
            conn.commit()

            return {'msg': 'Score added successfully'}, 200
        except:
            return {'msg': 'Could not add score'}, 400
