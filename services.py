import psycopg2
from psycopg2.extensions import (cursor as Cursor, connection as Connection, ISOLATION_LEVEL_AUTOCOMMIT)
from psycopg2 import Error
from typing import Any

from config import (USER, PASSWORD, HOST, PORT)


class Connecting():
    def __init__(self) -> None:
        try:
            self.connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = self.connection.cursor()
            print('Connection success!')
            cursor.execute('CREATE DATABASE homework7;')
            print('Database Created!')
        except (Exception, Error) as e:
            print(f'Error {e}')

    def __new__(cls: type[Any]):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Connecting, cls).__new__(cls)

        return cls.instance

    def connect_db(self):
        try:
            self.connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                database='homework7',
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            print('Connection to database success')
        except (Exception, Error) as e:
            print(f'Error {e}')

    def create_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games(
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(30) UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    price DOUBLE PRECISION DEFAULT(60)
                );
                CREATE TABLE IF NOT EXISTS genres(
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(30) UNIQUE NOT NULL,
                    description TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS result(
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER REFERENCES games(id),
                    genre_id INTEGER REFERENCES genres(id)
                );
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    login VARCHAR(32) UNIQUE NOT NULL,
                    password VARCHAR(30) NOT NULL,
                    first_name VARCHAR(32) NOT NULL,
                    last_name VARCHAR(32) NOT NULL,
                    wallet DOUBLE PRECISION DEFAULT(0),
                    date_reg DATE DEFAULT(now())
                );
                CREATE TABLE IF NOT EXISTS codes(
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER REFERENCES games(id),
                    key VARCHAR(25) NOT NULL UNIQUE,
                    is_active BOOL DEFAULT(True)
                );
                CREATE TABLE IF NOT EXISTS admin(
                    id SERIAL PRIMARY KEY,
                    login VARCHAR(32) UNIQUE NOT NULL,
                    password VARCHAR(30) NOT NULL,
                    first_name VARCHAR(32) NOT NULL,
                    last_name VARCHAR(32) NOT NULL,
                    date_reg DATE DEFAULT(now())
                );
            """)
        self.connection.commit()
        print('Tables successfuly created!')

    def create_superuser(self, login, password, first_name, last_name):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO admin(login, password, first_name, last_name)
                    VALUES ('{login}', '{password}', '{first_name}', '{last_name}');
                """)
                self.connection.commit()
                print('Superuser created')
        except:
            print('Пользователь создан')

    def check_admin(self, login):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM admin WHERE login='{login}';
            """)
            data = cursor.fetchall()
        self.connection.commit()
        print(data)
        return data

    def registration(self, login, password, first_name, last_name):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO users(login, password, first_name, last_name)
                VALUES ('{login}', '{password}', '{first_name}', '{last_name}');
            """)
        self.connection.commit()
        print('Registration success!')

    def check_user(self, login):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM users WHERE login='{login}';
            """)
            data = cursor.fetchall()
        self.connection.commit()
        print(data)
        return data

    def add_key(self, game_id, key):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO codes(game_id, key)
                VALUES ({game_id}, '{key}');
            """)
        self.connection.commit()
        print('Key added!')

    def set_genres(self, title, description):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO genres(title, description)
                VALUES ('{title}','{description}');
            """)
        self.connection.commit()
        print('Row has added to genre')

    def get_genres(self):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT * FROM genres;')
            data = cursor.fetchall()
        self.connection.commit()
        return data

    def set_game(self, title, description, price):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO games(title, description, price)
                VALUES ('{title}', '{description}', {price});
            """)
        self.connection.commit()
        print('Game added!')

    def get_games(self):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute('SELECT * FROM games;')
            data = cursor.fetchall()
        self.connection.commit()
        return data

    def get_game_id(self, title):
        data: tuple = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM games WHERE title='{title}';
            """)
            data = cursor.fetchall()
        self.connection.commit()
        return data

    def res(self, game_id, genre_id):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO result(game_id, genre_id)
                VALUES ({game_id}, {genre_id});
            """)
        self.connection.commit()
        print('ADDED!')

    def list_result(self):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT games.id, games.title, games.description, genres.title, genres.description, games.price FROM result
                INNER JOIN games ON result.game_id = games.id
                INNER JOIN genres ON result.genre_id = genres.id;
            """)
            data = cursor.fetchall()
        self.connection.commit()
        return data

    def check_buy(self, game_id):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM codes WHERE game_id = {game_id} AND is_active = true;
            """)
            data = cursor.fetchall()
        self.connection.commit()
        return data

    def buy(self, price, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE users SET wallet = wallet - {price} WHERE id={user_id};
            """)
        self.connection.commit()
        print('Игра куплена')

    def key_send(self, game_id):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE codes SET is_active = false WHERE game_id={game_id};
            """)
        self.connection.commit()
        print('Ключ ушел')