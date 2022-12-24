from flask import (
    Flask, 
    render_template, 
    request, 
    redirect,
    )
from werkzeug.security import check_password_hash
from services import Connecting


app = Flask(__name__)
conn: Connecting = Connecting()

conn.connect_db()
conn.create_tables()
conn.create_superuser('genitalgrinder90@gmail.com' ,'Brick92', 'root', 'Brick', '92')

user_id = ''
admin_id = ''


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
        elif login == data[0][2] and check_password_hash(data[0][3], password) == False:
            message = 'Неправильный пароль'
            return render_template('autorization.html', message=message)
        elif login == data[0][2] and check_password_hash(data[0][3], password) == True:
            user_id = data[0][0]
            return redirect('/shop')
    return render_template('autorization.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        login = request.form.get('login')
        password = request.form.get('password')
        check_password = request.form.get('check_password')
        data = conn.check_user(login)
        mail_data = conn.check_user_mail(email)
        if password != check_password:
            message = 'ПАРОЛИ НЕ СОВПАДАЮТ'
            return render_template('registration.html', message=message)
        elif data:
            message = 'ЛОГИН ЗАНЯТ'
            return render_template('registration.html', message=message)
        elif mail_data:
            message = 'Данный адрес уже зарегистрирован'
            return render_template('registration.html', message=message)
        elif not data and not mail_data and password == check_password:
            conn.registration(email, login, password, first_name, last_name)
            return redirect('/')
    return render_template('registration.html')

@app.route('/shop')
def search():
    global user_id
    data = conn.get_games()
    return render_template('shop.html', data=data, user_id=user_id)

@app.route('/shop/<int:id>', methods=['GET', 'POST'])
def get_game(id):
    global user_id
    if not user_id:
        return redirect('/')
    message = ''
    data = conn.list_result()
    basket_data = conn.check_add_in_basket(id)
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
            if not basket_data:
                conn.add_to_basket(user_id, id)
                message = 'добавлено в корзину'
                return render_template('game.html', result=result, message=message)
            else:
                message = 'товар уже добавлен'
                return render_template('game.html', result=result, message=message)
    return render_template('game.html', result=result)

@app.route('/shop/basket', methods=['GET', 'POST'])
def basket():
    global user_id
    if not user_id:
        return redirect('/')
    message = ''
    summ = 0
    data = conn.check_basket()
    if request.method == 'POST':
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
            conn.add_game_to_user(user_id, j, key[0])
        conn.buy(summ, user_id)
        return render_template('basket.html', data=data, message=message)
    return render_template('basket.html', data=data, message=message)

@app.route('/personal-cab/<int:id>', methods=['GET','POST'])
def personal_cab(id):
    global user_id
    if not user_id:
        return redirect('/')
    message = ''
    personal_data = conn.get_user(id)
    games_data = conn.get_user_games(id)
    if request.method == 'POST':
        money = request.form.get('money')
        if int(money) > 0:
            conn.art_money(user_id, money)
            message = 'success'
            return render_template('user-cab.html', p_data=personal_data, g_data=games_data, message=message, id=user_id)
    return render_template('user-cab.html', p_data=personal_data, g_data=games_data, id=user_id)

@app.route('/personal-cab/<int:id>/friends', methods=['GET', 'POST'])
def friends(id):
    global user_id
    if not user_id:
        return redirect('/')
    message = ''
    if request.method == 'POST':
        add_friend = request.form.get('add_friend')
        search = conn.search_friend(add_friend)
        if search:
            message = 'Найден пользователь'
            return render_template('friends.html', id=user_id, message=message, search=search)
        message = 'Пользователь не найден'
        return render_template('friends.html', id=user_id, message=message, search=search)
    return render_template('friends.html', id=user_id)
    
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global admin_id
    message = ''
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        data = conn.check_admin(login)
        hash = check_password_hash(data[0][3], password)
        if not data:
            message = 'Ты не админ, Вали отсюда'
            return render_template('admin.html', message=message)
        elif login == data[0][1] and hash == False:
            message = 'Неправильный пароль'
            return render_template('admin.html', message=message)
        elif login == data[0][2] and hash == True:
            admin_id = data[0][0]
            return redirect('/admin/ok')
    return render_template('admin.html')

@app.route('/admin/ok')
def admin_ok():
    global admin_id
    if not admin_id:
        return redirect('/admin')
    return ('<h2><a href="/admin/ok/set-genres">Добавьте жанры</a></h2><h2><a href="/admin/ok/add-game">Добавьте игры</h2><h2><a href="/admin/ok/add-key">Добавить ключи</a></h2>')

@app.route('/admin/ok/set-genres', methods=['GET', 'POST'])
def add_genre():
    global admin_id
    if not admin_id:
        return redirect('/admin')
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

@app.route('/admin/ok/add-key', methods=['GET', 'POST'])
def add_key():
    global admin_id
    if not admin_id:
        return redirect('/admin')
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

@app.route('/admin/ok/add-game', methods=['GET', 'POST'])
def add_game():
    global admin_id
    if not admin_id:
        return redirect('/admin')
    message = ''
    genre_data = conn.get_genres()
    games_data = conn.get_games()
    result = conn.list_result()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        genres = request.form.getlist('genre')
        if title and description and genres and title not in games_data:
            conn.set_game(title, description, price)
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