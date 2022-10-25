import json
from PyQt5 import QtWidgets, QtCore
import clientui
import requests
from PyQt5 import uic
from datetime import datetime
import socketio
from time import time

# connect to socket
sio = socketio.Client(logger=True, engineio_logger=True)
sio.connect('http://127.0.0.1:5000')


class LoginWindow(QtWidgets.QDialog, clientui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('messenger_loginui.ui', self)
        self.username = None
        self.entrance_button.pressed.connect(self.button_entr_pushed)

    def button_entr_pushed(self):
        self.username = self.login_line_edit.text()
        password = self.password_line_edit.text()
        pack = {'username': self.username, 'password': password}
        try:
            response = requests.post('http://127.0.0.1:5000/login', json=pack)
            if response.json()["result"]["status"] == "wrong password":
                self.label_3.setText("\nНеверный пароль, попробуйте еще раз")
            elif response.json()["result"]["status"] == "ok":
                print("Successfully login")
                self.open_main_window()
        except Exception as e:
            print(e)

    def open_main_window(self):
        global second_win

        second_win = MessengerWindow(self.username)
        second_win.show()

        self.close()


class MessengerWindow(QtWidgets.QMainWindow, clientui.Ui_MainWindow):
    def __init__(self, user):
        super().__init__()
        uic.loadUi('messenger.ui', self)
        self.username = user
        self.label_username.setText(self.username)
        self.pushButton.pressed.connect(self.button_pushed)
        self.first_load_msgs()
        self.label_status.setText("online")
        sio.send({'username': 'Service message',
                  'text': 'User ' + str(self.username) + ' has connected!',
                  "time": int(time())})
        # get messages from DB every 5 seconds
        # self.after = 0
        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.update_messages)
        # self.timer.start(5000)

    def first_load_msgs(self):
        # load messages from DB when starting the application
        responce = requests.get(f'http://127.0.0.1:5000/messages/0')
        for i in responce.json()['messages']:
            self.print_message(i)
            # self.after = i[0]

    def button_pushed(self):
        # send button click handler
        text = self.textEdit.toPlainText().strip()
        if text != "":
            self.send_message(text)
            self.textEdit.setText('')
            self.textEdit.repaint()

    def send_message(self, text):
        # send msg to socket and save in DB
        message = {'username': self.username, 'text': text}
        try:
            sio.send({'username': self.username, 'text': text, "time": int(time())})
            response = requests.post('http://127.0.0.1:5000/send_msg', json=message)
            if not response.json()["ok"]:
                self.show_text("Error while sending message")
        except Exception as e:
            print(e)
            self.show_text("Connection to server error")

    @staticmethod
    @sio.on('connect')
    def conn():
        second_win.label_status.setText("online")

    @staticmethod
    @sio.on('disconnect')
    def disconn():
        second_win.label_status.setText("offline")

    @staticmethod
    @sio.on('message')
    def update_messages(mes):
        # show msg when receiving it from socket
        MessengerWindow.print_message(second_win, message=mes)
        # get messages from DB every n seconds
        # try:
        #     response = requests.get(f'http://127.0.0.1:5000/messages/{self.after}')
        #     data = response.json()
        #     if len(data['messages']) > 0:
        #         for message in data['messages']:
        #             if self.after < message[0]:
        #                 self.print_message(message)
        #             self.after = message[0]
        # except Exception as e:
        #     print(e)
        #     self.show_text("Connection error!")

    def print_message(self, message):
        if type(message) == str:
            message = json.loads(message)
        try:
            self.show_text(f"{message['username']}   " +
                           f"{datetime.fromtimestamp(message['time']).strftime('%H:%M:%S')}" 
                           f"\n{message['text']}\n")
        except Exception as e:
            print(e)

    def show_text(self, text):
        self.textBrowser.append(text)


app = QtWidgets.QApplication([])
second_win = MessengerWindow("")
window = LoginWindow()
window.show()
app.exec_()
