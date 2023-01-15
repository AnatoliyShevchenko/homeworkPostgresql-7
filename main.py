from flask import (
    Flask, 
    render_template, 
    request, 
    redirect,
    flash
    )
from werkzeug.security import check_password_hash
from flask_login import LoginManager, login_user, current_user, login_required
from userlogin import UserLogin
from services import Connecting
import os


app = Flask(__name__)
app.secret_key = os.urandom(50)
conn: Connecting = Connecting()
login_manager = LoginManager(app)

conn.connect_db()
conn.create_tables()
conn.create_superuser('genitalgrinder90@gmail.com' ,'Brick92', 'root')


@login_manager.user_loader
def load_user(id):
    print('load_user')
    return UserLogin().fromDB(id)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        data = conn.check_user(login)
        if not data:
            message = 'Данный логин не зарегистрирован'
            return render_template('autorization.html', message=message)
        elif login == data[0][2] and check_password_hash(data[0][3], password) == False:
            message = 'Неправильный пароль'
            return render_template('autorization.html', message=message)
        elif login == data[0][2] and check_password_hash(data[0][3], password) == True:
            userlogin = UserLogin().create(data[0])
            login_user(userlogin)
            user_id = current_user.get_id()
            token = conn.generate_token()
            conn.autorization(user_id, token)
            is_admin = conn.check_admin(login)
            if is_admin:
                flash(user_id)
                flash(token)
                return redirect('/admin')
            flash(user_id)
            flash(token)
            return redirect('/shop')
    return render_template('autorization.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        login = request.form.get('login')
        password = request.form.get('password')
        data = conn.check_user(login)
        mail_data = conn.check_user_mail(email)
        if data:
            message = 'ЛОГИН ЗАНЯТ'
            return render_template('registration.html', message=message)
        elif mail_data:
            message = 'Данный адрес уже зарегистрирован'
            return render_template('registration.html', message=message)
        elif not data and not mail_data and password:
            conn.registration(email, login, password)
            return redirect('/')
    return render_template('registration.html')

@app.route('/shop')
def search():
    data = conn.get_games()
    return render_template('shop.html', data=data)

@app.route('/shop/<int:game_id>', methods=['GET', 'POST'])
def get_game(game_id):
    message = ''
    data = conn.list_result()
    basket_data = conn.check_add_in_basket(game_id)
    result: list[tuple] = []
    for i in data:
        if i[0] == int(game_id):
            price = i[5]
            result.append(i)
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        data = conn.check_buy(game_id)
        if not data:
            message = 'извините ключей не осталось'
            return render_template('game.html', result=result, message=message)
        elif data:
            if not basket_data:
                conn.add_to_basket(user_id, game_id)
                message = 'добавлено в корзину'
                return render_template('game.html', result=result, message=message)
            else:
                message = 'товар уже добавлен'
                return render_template('game.html', result=result, message=message)
    return render_template('game.html', result=result)

@app.route('/shop/basket', methods=['GET', 'POST'])
def basket():
    message = ''
    summ = 0
    data = conn.check_basket()
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        games = request.form.getlist('id_game')
        for i in games:
            price: float = conn.get_price(i)
            summ += price[0]
        print(summ)
        user_money = conn.check_money(user_id)
        if user_money[0] < summ:
            message = 'У вас недостаточно средств'
            return render_template('basket.html', data=data, message=message)
        message = 'Поздравляем с приобретением!'
        for j in games:
            key = conn.get_key(j)
            conn.key_send(key[0])
            conn.add_game_to_user(user_id, j, key[1])
        conn.buy(summ, user_id)
        return render_template('basket.html', data=data, message=message)
    return render_template('basket.html', data=data, message=message)

@app.route('/personal-cab/<int:user_id>', methods=['GET','POST'])
def personal_cab(user_id):
    message = ''
    personal_data = conn.get_user(user_id)
    games_data = conn.get_user_games(user_id)
    if request.method == 'POST':
        money = request.form.get('money')
        if int(money) > 0:
            conn.art_money(user_id, money)
            message = 'success'
            return render_template('user-cab.html', p_data=personal_data, g_data=games_data, message=message)
    return render_template('user-cab.html', p_data=personal_data, g_data=games_data)

@app.route('/personal-cab/<int:id>/friends', methods=['GET', 'POST'])
def friends(id):
    id = user_id
    message = ''
    if request.method == 'POST':
        add_friend = request.form.get('add_friend')
        search = conn.search_friend(add_friend)
        if search:
            message = 'Найден пользователь'
            return render_template('friends.html', message=message, search=search)
        message = 'Пользователь не найден'
        return render_template('friends.html', message=message, search=search)
    return render_template('friends.html')
    
@app.route('/admin')
def admin():
    token = request.args.get('token')
    user_id = request.args.get('user_id')
    return render_template('admin.html', user_id=user_id, token=token)

@app.route('/admin/set-genres', methods=['GET', 'POST'])
def add_genre():
    message = ''
    data = conn.get_genres()
    if request.method == 'POST':
        title = request.form.get('title')
        if title:
            message = 'Genre was added'
            conn.set_genres(title)
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
        code_data = conn.check_key(key)
        if len(key) != 25:
            message = 'Длина ключа должна быть 25 символов'
            return render_template('add-key.html', result=result, message=message, data=data)
        elif not game:
            message = 'Игра не выбрана'
            return render_template('add-key.html', result=result, message=message, data=data)
        elif code_data:
            message = 'Ключ уже добавлен'
            return render_template('add-key.html', result=result, message=message, data=data)
        elif len(key) == 25 and data and not code_data:
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
        year = request.form.get('year')
        genres = request.form.getlist('genre')
        if title and description and genres and title not in games_data:
            conn.set_game(title, description, year, price)
            message = 'Game added!'
            game = conn.get_game_id(title)
            game_id = game[0][0]
            for i in genres:
                conn.res(game_id, i)
        elif not title or not description or not genres or title in games_data:
            message = 'fields must not be empty'
            return render_template('add-game.html', genre_data=genre_data, result=result, message=message)
    return render_template('add-game.html', genre_data=genre_data, result=result, message=message)


if __name__ == '__main__':
    app.run(port=1234, debug=True)