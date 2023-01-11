from services import Connecting


conn: Connecting = Connecting()


class UserLogin():
    def fromDB(self, id):
        data = conn.get_user(id)
        self.__user = data[0]
        return self

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
        return (self.__user[0])