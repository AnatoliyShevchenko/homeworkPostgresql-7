import psycopg2
from psycopg2.extensions import (cursor as Cursor, connection as Connection, ISOLATION_LEVEL_AUTOCOMMIT)
from psycopg2 import Error
from werkzeug.security import generate_password_hash
from typing import Any
import os

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
            cursor.execute('CREATE DATABASE homework7mvc;')
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
                database='homework7mvc',
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
                    year_of_issue INTEGER NOT NULL,
                    price DOUBLE PRECISION DEFAULT(60)
                );
                CREATE TABLE IF NOT EXISTS genres(
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(30) UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS result(
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER REFERENCES games(id),
                    genre_id INTEGER REFERENCES genres(id)
                );
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(60) UNIQUE NOT NULL,
                    login VARCHAR(32) UNIQUE NOT NULL,
                    password VARCHAR(200) NOT NULL,
                    wallet DOUBLE PRECISION DEFAULT(0),
                    date_reg DATE DEFAULT(now()),
                    is_admin BOOL DEFAULT(False),
                    is_manager BOOL DEFAULT(False),
                    source VARCHAR(30) DEFAULT('main')
                );
                CREATE TABLE IF NOT EXISTS codes(
                    id SERIAL PRIMARY KEY,
                    game_id INTEGER REFERENCES games(id),
                    key VARCHAR(25) NOT NULL UNIQUE,
                    is_active BOOL DEFAULT(True)
                );
                CREATE TABLE IF NOT EXISTS user_games(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    game_id INTEGER REFERENCES games(id),
                    code_id INTEGER REFERENCES codes(id)
                );
                CREATE TABLE IF NOT EXISTS basket(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    game_id INTEGER REFERENCES games(id)
                );
                CREATE TABLE IF NOT EXISTS autorization(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    token text UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS invite(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    friend_id INTEGER REFERENCES users(id)
                );
                CREATE TABLE IF NOT EXISTS friends(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    friend_id INTEGER REFERENCES users(id)
                );
            """)
        self.connection.commit()
        print('Tables successfuly created!')

    def generate_token(self):
        token = os.urandom(512).hex()
        return token

    def autorization(self, user_id, token):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO autorization(user_id, token)
                VALUES ({user_id}, '{token}');
            """)
        self.connection.commit()
        print('Авторизация выполнена')

    def check_token(self, token):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM autorization WHERE token='{token}';
            """)
            data = cursor.fetchone()
        self.connection.commit()
        print(data)
        return data

    def create_superuser(self, email, login, password):
        try:
            hash_password = generate_password_hash(password)
            with self.connection.cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO users(email, login, password, is_admin, is_manager)
                    VALUES ('{email}', '{login}', '{hash_password}', True, True);
                """)
                self.connection.commit()
                print('Superuser created')
        except:
            print('Пользователь создан')

    def check_admin(self, login):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM users WHERE login='{login}' AND is_admin=True;
            """)
            data = cursor.fetchall()
        self.connection.commit()
        print(data)
        return data

    def registration(self, email, login, password):
        hash_password = generate_password_hash(password)
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO users(email, login, password)
                VALUES ('{email}','{login}', '{hash_password}');
            """)
        self.connection.commit()
        print('Registration success!')

    def check_user(self, login):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, email, login, password, wallet FROM users WHERE login='{login}';
            """)
            data = cursor.fetchall()
        self.connection.commit()
        print(data)
        return data

    def check_user_mail(self, email):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM users WHERE email='{email}';
            """)
            data = cursor.fetchall()
        self.connection.commit()
        print(data)
        return data

    def get_user(self, id):
        data = ()
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM users WHERE id={id};
            """)
            data = cursor.fetchone()
        self.connection.commit()
        print(data)
        return data

    def get_user_games(self, id):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT users.login, games.title, codes.key FROM user_games
                INNER JOIN users ON user_games.user_id = users.id
                INNER JOIN games ON user_games.game_id = games.id
                INNER JOIN codes ON user_games.code_id = codes.id
                WHERE user_games.user_id = {id};
            """)
            data = cursor.fetchall()
        self.connection.commit()
        return data
      
    def art_money(self, id, money):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE users SET wallet = wallet + {money} WHERE id={id};
            """)
        self.connection.commit()
        print('cash shower!')

    def check_key(self, key):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT * FROM codes WHERE key='{key}';
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

    def set_genres(self, title):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO genres(title)
                VALUES ('{title}');
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

    def set_game(self, title, description, year, price):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO games(title, description, year_of_issue, price)
                VALUES ('{title}', '{description}', {year}, {price});
            """)
        self.connection.commit()
        print('Game added!')

    def check_money(self, user_id):
        data = ()
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT wallet FROM users WHERE id={user_id};
            """)
            data = cursor.fetchone()
        self.connection.commit()
        return data

    def get_price(self, game_id):
        data = ()
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT price FROM games WHERE id={game_id};
            """)
            data = cursor.fetchone()
        self.connection.commit()
        return data

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
                SELECT games.id, games.title, games.description, genres.title, games.year_of_issue, games.price FROM result
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
            data = cursor.fetchone()
        self.connection.commit()
        return data

    def add_to_basket(self, user_id, game_id):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO basket(user_id, game_id)
                VALUES ({user_id}, {game_id});
            """)
        self.connection.commit()
        print('Игра добавлена в корзину')

    def check_basket(self):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT games.id, games.title, games.description, games.price FROM basket
                INNER JOIN games ON basket.game_id = games.id;
            """)
            data = cursor.fetchall()
        self.connection.commit()
        return data

    def check_add_in_basket(self, game_id):
        data: tuple = ()
        with self.connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM basket WHERE game_id={game_id};")
            data = cursor.fetchone()
        self.connection.commit()
        return data

    def clear_basket(self):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM basket;")
        self.connection.commit()
        print('Корзина очищена')

    def buy(self, price, user_id):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE users SET wallet = wallet - {price} WHERE id={user_id};
            """)
        self.connection.commit()
        print('Игра куплена')

    def get_key(self, game_id):
        data: list[tuple] = []
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT key, id FROM codes WHERE game_id = {game_id} and is_active = True;
            """)
            data = cursor.fetchone()
        self.connection.commit()
        print(data)
        return data

    def key_send(self, key):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE codes SET is_active = false WHERE key = '{key}' and is_active = True;
            """)
        self.connection.commit()
        print('Ключ ушел')

    def add_game_to_user(self, user_id, game_id, code_id):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO user_games(user_id, game_id, code_id)
                VALUES ({user_id}, {game_id}, '{code_id}');
            """)
        self.connection.commit()
        print('Игра добавлена пользователю')

    def search_friend(self, add_friend):
        data = ()
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT email, login FROM users WHERE login = '{add_friend}' OR email = '{add_friend}';
            """)
            data = cursor.fetchone()
        self.connection.commit()
        return data