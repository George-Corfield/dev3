from encryption import Hashing_algorithm

class User():
    def __init__(self, username, password, UserID, OrgID, StatusID, ROLE):
        self.username = username #sets username
        self.password = password #sets password
        self.userID = UserID #sets userID
        self.orgID = OrgID #sets orgID
        
        self.statusID = StatusID #sets statusID
        self.permission = ROLE #sets roleID
        self.active = True #keeps account active for session
        self.authenticated = True #allows user to access web pages
    
    def is_authenticated(self):
        #returns as true upon initialisation as user is authenticated
        return self.authenticated

    def is_active(self):
        #returns true until user logs off
        return self.active

    def is_anonymous(self):
        #do not require anonymous users 
        return False

    def get_id(self):
        #returns userID easily
        return self.userID

    def is_admin(self):
        #normal user not admin
        return False

    def validate(self, password):
        #validates password with entered password
        h = Hashing_algorithm()
        h.update(password) #hashes password entered
        return True if h.hexdigest() == self.password else False
        #returns true if they match, false if not

        


class Admin(User):
    def __init__(self,username,password,UserID,OrgID,StatusID, ROLE):
        super().__init__(username,password,UserID,OrgID,StatusID,ROLE)

    def is_admin(self):
        return True





