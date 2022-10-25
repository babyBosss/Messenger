import time
from flask import Flask, request, abort, render_template, url_for, redirect, jsonify, g, flash
import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from User import User
from Database import DataBase
from config import host, user, password, db_name
import psycopg2
from flask_socketio import SocketIO, send, emit
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

messages = []
users = {}
SECRET_KEY = 'hard to guess string'
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager(app)
# переадресация для неавторизованных
login_manager.login_view = 'login'
login_manager.login_message = "Авторизируйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


# accepts from the client {'username':'', text:'', 'time':''}
# and send to other clients
@socketio.on('message')
def handle_message(data):
    print(f"Message: {data}")
    send(data, broadcast=True)


@login_manager.user_loader
def load_user(user_id):
    return User().fromdB(user_id, dbase)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name)
        except Exception as e:
            print("DB error connection: ", e)
    return db


# connect DB before each request
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = DataBase(db)

# close DB connection
@app.teardown_appcontext
def close_connection(exception):
    """Закрывает соединение с с БД"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/status')
def status():
    return {
        'status': True,
        'name': 'Messenger',
        'time': datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        'messages_count': len(messages),
        'users_count': len(users)
    }


# save message to database
# accepts from the client by post method json{'text=':''}
@app.route('/send_msg', methods=['POST'])
def send_msg():
    user_id = current_user.get_id()
    if user_id is None:
        try:
            username = request.json['username']
            user_id = dbase.get_user_by_name(username)[0]
        except:
            print("Пользователь не опознан")
            return {"ok": False, "reason": "no user found"}
    print("user_id= ", user_id)
    text = request.json['text']
    message = {'user_id': user_id, 'text': text}
    dbase.add_msg(message)
    return {'ok': True}


@app.route('/messages/<after>')
def messages_view(after):
    filtred_messages = dbase.get_messages_after(after)
    print(filtred_messages)
    return {'messages': filtred_messages}

# main page on browser version
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def messenger():
    old_messages = []
    if request.method == "GET":
        old_messages = dbase.get_old_messages()

    return render_template("mainpage.html", username=current_user.get_name(), old_messages=old_messages)


# accept from client by post method json{"username":"", "password":""}
# login user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.json['username']
        password = request.json['password']
        user = dbase.get_user_by_name(username)
        if user:
            # если уже есть в бд
            if user[2] == password:
                user_login = User().create(user)
                login_user(user_login, remember=True)
            else:
                flash("Неправильный пароль")
                return jsonify(result={'status': 'wrong password'})
        # регистрация нового пользователя
        else:
            registration = dbase.add_user(username, password)
            if registration:
                user = dbase.get_user_by_name(username)
                user_login = User().create(user)
                login_user(user_login, remember=True)
            else:
                print("error registration")
        return jsonify(result={'link': 'http://127.0.0.1:5000/chat', 'status': 'ok'})
    else:
        # todo повторный ввод пароля
        return render_template("loginpage.html")


@app.route('/logout/')
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


if __name__ == "__main__":

    socketio.run(app, port=5000,log_output=True)

    # ,allow_unsafe_werkzeug=True