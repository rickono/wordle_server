import csv
from connect import connect
import psycopg2.extras
import bcrypt
import random
import string

print('POPULATING USERS')

with open('data/users.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    conn = connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    for row in reader:
        username = row['username']
        name = row['user_name']
        email = row['email']
        password = row['password']
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)

        sql = """INSERT INTO users (username, name, hashed_password)
        VALUES (%s, %s, %s)"""

        cur.execute(sql, (username, name, hashed))
    conn.commit()

conn = connect()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
print('POPULATING GAMES')
for i in range(100):
    word = ''.join([random.choice(string.ascii_letters) for c in range(5)])
    lie_rate = random.randint(0, 100)
    sql = 'INSERT INTO games (word, lie_rate) VALUES (%s, %s)'
    cur.execute(sql, (word, lie_rate))

conn.commit()


conn = connect()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
print('POPULATING SCORES')
for i in range(1000):
    random_game = """SELECT *
	FROM games
	ORDER BY random()
	LIMIT 1;"""
    cur.execute(random_game)
    game = cur.fetchone()
    random_user = """SELECT *
	FROM users
	ORDER BY random()
	LIMIT 1;"""
    cur.execute(random_user)
    user = cur.fetchone()
    score = random.randint(1, 10)
    time = random.randint(400, 800)
    guesses = [''.join([random.choice(string.ascii_letters)
                        for c in range(5)]) for i in range(5)]

    guesses.append(game['word'])
    insert_scores = 'INSERT INTO scores (user_id, game_id, score, time, guesses) VALUES (%s, %s, %s, %s, %s)'
    cur.execute(insert_scores,
                (user['user_id'], game['game_id'], score, time, guesses))

conn.commit()
