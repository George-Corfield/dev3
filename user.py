import hashlib
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, password, UserID, OrgID):
        self.username = username
        self.password = password
        self.userID = UserID
        self.orgID = OrgID
        self.is_active = True
        self.is_authenticated = True
    
    def is_authenticated(self):
        return self.is_authenticated

    def is_active(self):
        return self.is_active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.userID

    def check_password(self, password):
        h = hashlib.sha256(bytes(password.encode()))
        return True if h.hexdigest() == self.password else False

