import hashlib

class User:
    def __init__(self, username, password, UserID, OrgID):
        self.username = username
        self.password = password
        self.userID = UserID
        self.orgID = OrgID
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.userID

    def check_password(self, password):
        h = hashlib.sha256(bytes(password.encode()))
        return True if h.hexdigest() == self.password else False

