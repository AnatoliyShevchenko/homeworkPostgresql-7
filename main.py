from flask import (Flask, render_template, request, redirect)
from services import Connecting


app = Flask(__name__)
conn: Connecting = Connecting()

conn.connect_db()
conn.create_tables()
conn.create_superuser('Brick92', 'root', 'Brick', '92')

user_id = ''

@app.route('/', methods=['GET', 'POST'])
def main():
    global user_id
    message = ''
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        data = conn.check_user(login)
        if not data:
            message = 'Данный логин не зарегистрирован'
            return render_template('autorization.html', message=message)
        elif login == data[0][1] and password != data[0][2]:
            message = 'Неправильный пароль'
            return render_template('autorization.html', message=message)
        elif login == data[0][1] and password == data[0][2]:
            user_id = data[0][0]
            return redirect('/shop')
    return render_template('autorization.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    message = ''
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        login = request.form.get('login')
        password = request.form.get('password')
        check_password = request.form.get('check_password')
        data = conn.check_user(login)
        if password != check_password:
            message = 'ПАРОЛИ НЕ СОВПАДАЮТ'
            return render_template('registration.html', message=message)
        elif data:
            message = 'ЛОГИН ЗАНЯТ'
            return render_template('registration.html', message=message)
        elif not data and password == check_password:
            conn.registration(login, password, first_name, last_name)
            return redirect('/')
    return render_template('registration.html')

@app.route('/shop')
def search():
    data = conn.get_games()
    return render_template('shop.html', data=data)

@app.route('/shop/<int:id>', methods=['GET', 'POST'])
def get_game(id):
    global user_id
    message = ''
    data = conn.list_result()
    result: list[tuple] = []
    for i in data:
        if i[0] == int(id):
            price = i[5]
            result.append(i)
    if request.method == 'POST':
        data = conn.check_buy(id)
        if not data:
            message = 'извините ключей не осталось'
            return render_template('game.html', result=result, message=message)
        elif data:
            conn.buy(price, user_id)
            conn.key_send(id)
            message = 'Поздравляем, вы приобрели ключ'
            return render_template('game.html', message=message, result=result)
    return render_template('game.html', result=result)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = ''
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        data = conn.check_admin(login)
        if not data:
            message = 'Ты не админ, Вали отсюда'
            return render_template('admin.html', message=message)
        elif login == data[0][1] and password != data[0][2]:
            message = 'Неправильный пароль'
            return render_template('admin.html', message=message)
        elif login == data[0][1] and password == data[0][2]:
            return redirect('/admin/ok')
    return render_template('admin.html')

@app.route('/admin/ok')
def admin_ok():
    return ('<h2><a href="/admin/set-genres">Добавьте жанры</a></h2><h2><a href="/admin/add-game">Добавьте игры</h2><h2><a href="/admin/add-key">Добавить ключи</a></h2>')

@app.route('/admin/set-genres', methods=['GET', 'POST'])
def add_genre():
    message = ''
    data = conn.get_genres()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        if title and description:
            message = 'Genre was added'
            conn.set_genres(title, description)
            return render_template('set-genres.html', data=data, message=message)
        message = 'Fields must be not empty'
        return render_template('set-genres.html', data=data, message=message)
    
    return render_template('set-genres.html', data=data)

@app.route('/admin/add-key', methods=['GET', 'POST'])
def add_key():
    message = ''
    result = conn.list_result()
    data = conn.get_games()
    if request.method == 'POST':
        key = request.form.get('key')
        game = request.form.get('game')
        if len(key) != 25:
            message = 'Длина ключа должна быть 25 символов'
            return render_template('add-key.html', result=result, message=message, data=data)
        elif not game:
            message = 'Игра не выбрана'
            return render_template('add-key.html', result=result, message=message, data=data)
        elif len(key) == 25 and data:
            conn.add_key(game, key)
            message = 'Ключ добавлен'
            return render_template('add-key.html', result=result, message=message, data=data)
    return render_template('add-key.html', result=result, message=message, data=data)

@app.route('/admin/add-game', methods=['GET', 'POST'])
def add_game():
    message = ''
    genre_data = conn.get_genres()
    games_data = conn.get_games()
    result = conn.list_result()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        genres = request.form.getlist('genre')
        if title and description or title not in games_data:
            conn.set_game(title, description, price)
            message = 'Game added!'
            game = conn.get_game_id(title)
            game_id = game[0][0]
            for i in genres:
                conn.res(game_id, i)
    return render_template('add-game.html', genre_data=genre_data, result=result, message=message)


if __name__ == '__main__':
    app.run(port=1234, debug=True)