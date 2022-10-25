from datetime import datetime

from flask import jsonify

class DataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_user_by_id(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = '{user_id}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except:
            print("Ошибка получения данных о пользователе")
        return False


    def get_user_by_name(self, name):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE username = '{name}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except:
            print("Ошибка получения данных о пользователе")
        return False

    def add_user(self, name, password):
        try:
            self.__cur.execute("INSERT INTO users (username,password) VALUES(%s,%s)", (name,password))
            self.__db.commit()
        except:
            print("Ошибка добавления пользователя в БД")
            return False
        return True

    def add_msg(self, msg):
        #  {'user_id': user_id, 'text': text, 'time': current_time}
        try:
            # self.__cur.execute(f"-- SELECT * FROM users WHERE id = '{msg[0]}' LIMIT 1")
            # name = self.__cur.fetchone()
            print("to db : ", msg)
            self.__cur.execute("INSERT INTO msgs (id_sender,message,datetime) VALUES(%s,%s,%s);", (int(msg["user_id"]), msg["text"], 'now'))
            self.__db.commit()
        except:
            print("Ошибка добавления сообщения в БД")
            return False
        return True

    def get_old_messages(self):
        try:
            self.__cur.execute(f"select id_msg,username,message,datetime from msgs join users u on u.id = msgs.id_sender;")
            # res = self.__cur.fetchall()
            res = [{"id": i[0], "username":i[1], "text":i[2], "time": str(i[3].strftime("%H:%M:%S"))} for i in self.__cur.fetchall()]            # print(res)
            # print(jsonify(res))
            return res
        except Exception as e:
            print("Ошибка get_old_messages", e)
            return []

    def get_messages_after(self, msg_num):
        try:
            self.__cur.execute(f"select id_msg,username,message,datetime from msgs join users u on u.id = msgs.id_sender where id_msg > {int(msg_num)};")
            # res = self.__cur.fetchall()
            res = [{"id": i[0], "username":i[1], "text":i[2], "time": datetime.timestamp(datetime.fromisoformat(str(i[3])))} for i in self.__cur.fetchall()]

            # print(res)
            # print(jsonify(res))
            return res
        except Exception as e:
            print("Ошибка get_messages_after", e)
            return []
