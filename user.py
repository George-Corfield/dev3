from encryption import Hashing_algorithm
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, username, password, UserID, OrgID, StatusID, ROLE):
        self.username = username
        self.password = password
        self.userID = UserID
        self.orgID = OrgID
        self.statusID = StatusID
        self.permission = ROLE
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

    def is_admin(self):
        return False

    def check_password(self, password):
        h = Hashing_algorithm()
        h.update(password)
        return True if h.hexdigest() == self.password else False


class Admin(User):
    def __init__(self,username,password,UserID,OrgID,StatusID, ROLE):
        super().__init__(username,password,UserID,OrgID,StatusID,ROLE)

    def is_admin(self):
        return True

    




