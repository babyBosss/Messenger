
class User():
    # при запросе от браузера (user_loader)
    def fromdB(self, user_id, db):
        self.__user = db.get_user_by_id(user_id)
        return self
    # при авторизации на сайте
    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user[0])

    def get_name(self):
        try:
            n = str(self.__user[1])
            return n
        except:
            return ""
