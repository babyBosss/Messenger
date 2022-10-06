import time
from flask import Flask, request, abort
import datetime
#  pyuic5 messenger.ui -o clientui.py
app = Flask(__name__)
# messages = [{'username': '', 'text': '', 'time': ''}]
messages = []
users = {}

@app.route('/')
def hello():
    return 'Hello world'


@app.route('/status')
def status():
    return {
        'status': True,
        'name': 'Messenger',
        'time': datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        'messages_count': len(messages),
        'users_count': len(users)
    }


@app.route('/send', methods=['POST'])
def send():
    username = request.json['username']
    password = request.json['password']

    if username in users:
        if password != users[username]:
            return abort(401)
    else:
        users[username] = password
    print(users)
    text = request.json['text']
    current_time = time.time()
    message = {'username': username, 'text': text, 'time': current_time}
    messages.append(message)
    # print(messages)
    return {'ok': True}


@app.route('/messages')
def messages_view():
    after = float(request.args.get('after'))
    filtred_messages = [message for message in messages if message['time'] > after]

    return {
        'messages': filtred_messages
    }


app.run()
