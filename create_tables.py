from config import config
import psycopg2


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL
            )
        """,
        """ 
        CREATE TABLE IF NOT EXISTS games (
            game_id SERIAL PRIMARY KEY,
            word VARCHAR(255) NOT NULL,
            lie_rate INTEGER NOT NULL
            )
        """,
        """ 
        CREATE TABLE IF NOT EXISTS scores (
            score_id SERIAL PRIMARY KEY,
            game_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            time INTEGER NOT NULL,
            guesses VARCHAR(255)[] NOT NULL,
            FOREIGN KEY (user_id)
            REFERENCES users (user_id),
            FOREIGN KEY (game_id)
            REFERENCES games (game_id)
            )
        """
    )
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
