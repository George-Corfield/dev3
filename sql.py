import sqlite3 as sql
import hashlib

from flask_socketio import rooms
from user import User, Admin
from encryption import Hashing_algorithm
import json
import re

password_regex = r'''^(?=(.*[A-Z]){1,})(?=(.*[a-z]){1,})(?=(.*[0-9]){1,})(?=(.*[\W]){1,}).{8,18}$'''
email_regex = r'''\b[a-zA-Z0-9!#$%&'"*+-/;=?^_`|]+@[a-zA-Z0-9-.]+\.[a-zA-Z]{2,}\b'''

default_channels = ['#General','#Work','#Reminders']

MAX_USERS = 15


class db:
    def __init__(self, name):
        self.dbname = name+'.db'
        with sql.connect(self.dbname) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users
            (UserID INTEGER PRIMARY KEY,
             EMAIL TEXT,
             USERNAME TEXT,
             PASSWORD TEXT,
             OrgID INTEGER)
             ''')
            c.execute('''CREATE TABLE IF NOT EXISTS connections
            (ConnectionID INTEGER PRIMARY KEY,
             RoomID INTEGER,
             UserID INTEGER)''')
            c.execute('''CREATE TABLE IF NOT EXISTS messages
            (MessageID INTEGER PRIMARY KEY,
             MESSAGE TEXT,
             ConnectionID INTEGER)''')
            c.execute('''CREATE TABLE IF NOT EXISTS rooms
            (RoomID INTEGER PRIMARY KEY,
             ROOM TEXT,
             OrgID INTEGER,
             RoomType)''')
            c.execute('''CREATE TABLE IF NOT EXISTS organisation
            (OrgID INTEGER PRIMARY KEY,
            OrgPass TEXT,
            OrgName TEXT)''')
            conn.commit()
        conn.close()

    def save_user(self,username,password,email):
        if not re.fullmatch(password_regex,password):
            return 'Invalid Password'
        if not re.fullmatch(email_regex,email):
            return 'Invalid Email'
        h = hashlib.sha256(bytes(password.encode()))
        password = h.hexdigest()
        conn=sql.connect(self.dbname)
        c=conn.cursor()
        if self.username_exists(username) == 0:
            c.execute('''INSERT INTO users(EMAIL,USERNAME,PASSWORD,OrgID,statusID,RoleID) VALUES (?,?,?,?,?,?)''', (email,username,password,0,3,3))
            conn.commit()
        else:
            return 'Username already exists'
        conn.close()
        return None
    
    def create_org(self,org_name,org_pass,create_channels,userID):
        h = Hashing_algorithm()
        h.update(org_pass)
        org_pass = h.hexdigest() #hashes orgPass to be stored in database
        conn=sql.connect(self.dbname)
        #connects to database
        c=conn.cursor()
        if self.org_exists(org_name) == 0:
        #checks if org to be created exists or not
            c.execute('''INSERT INTO organisation(OrgPass,OrgName) VALUES (?,?)''', (org_pass,org_name,))
            #creates new record or organisation
            conn.commit()
            c.execute('''SELECT OrgID FROM organisation WHERE OrgName=?''',(org_name,))
            #selects just created orgID
            OrgID=c.fetchall()
            conn.commit()
            if create_channels: #if the user wants default channels to be created
                for channel in default_channels:
                #iterates through default channels list
                    c.execute('''INSERT INTO rooms(ROOM,OrgID,RoomType) VALUES (?,?,?)''',(channel,OrgID[0][0],'Public'))
                    #creates new room in rooms
                    conn.commit()
                    c.execute('''SELECT RoomID FROM rooms WHERE ROOM=? AND OrgID=?''',(channel,OrgID[0][0],))
                    #selects just created roomID from rooms
                    RoomID = c.fetchall()
                    conn.commit()
                    self.create_connection(RoomID[0][0],userID)
                    #creates connection between roomID and UserID
                     
            c.execute('''UPDATE users SET OrgID=?, RoleID=? WHERE UserID=?''',(OrgID[0][0],1,userID))
            #updates users Role and OrgID to new values, 1 = administrator
            conn.commit()
            conn.close()
            return None
        else:
            return 'Organisation Already Exists'
        
    
    def create_connection(self,RoomID,UserID):
        #creates new connection between room and user
        conn = sql.connect(self.dbname) #connects to database
        c = conn.cursor()
        c.execute('''INSERT INTO connections(RoomID,UserID) VALUES (?,?)''',(RoomID,UserID,))
        #creates new record in connections with roomID and UserID, connectionID incremented automatically
        conn.commit()
        conn.close()
        
    def connection_exists(self,RoomID,UserID):
        #checks if a connection between a room and user already exists
        conn = sql.connect(self.dbname) #connects to database
        c = conn.cursor()
        c.execute('''SELECT EXISTS (SELECT 1 FROM connections
                                    WHERE UserID=?
                                    AND RoomID = ?)''',
                    (UserID,RoomID,))
        #selects 1 if UserID and RoomID are related in connections
        #selects 0 if userID and RoomID are not related
        return c.fetchall()[0][0] #returns 1 or 0
    
    def create_room(self,RoomName,UserID,OrgID):
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        #connects to database
        try:
            c.execute('''INSERT INTO rooms(ROOM, OrgID, RoomType)
                    VALUES (?,?,?)''',(RoomName,OrgID,'Public'))
            #creates new record of public room with specified roomname and orgID
            rid = c.lastrowid #gets ID or last created row
            conn.commit()
            self.create_connection(rid,UserID) #creates connection between current user and roomID
            if self.connection_exists(rid,self.get_admin_id(OrgID)) != 1:
            #checks that there is not already a connection between admin user and room
                self.create_connection(rid,self.get_admin_id(OrgID))
                #if not creates connection between admin user and room (admin added to every room)
            conn.close()
            return None
        except:
            return 'Error creating room'        
        
    def join_org(self,orgName, orgPass, UserID):
        conn=sql.connect(self.dbname)
        #connects to database
        c = conn.cursor()
        if self.org_exists(orgName) == 1:
        #checks that the orgname is valid
            OrgID = self.get_org_id(orgName)
            #retrieves orgID of org with orgName
            c.execute('''SELECT OrgPass FROM organisation WHERE OrgID = ?''', (OrgID,))
            #selects hashed orgPass of organisation in database
            ExpectedOrgPass = c.fetchall()[0][0]; conn.commit()
            #stored orgPass
            h = Hashing_algorithm()
            h.update(orgPass)
            orgpass = h.hexdigest()
            #hashes given orgPass
            if orgpass == ExpectedOrgPass:
                #checks they match
                c.execute('''UPDATE users SET OrgID=?, RoleID=? WHERE UserID=?''',(OrgID,2,UserID,))
                #sets users orgID 
                conn.commit()
                for channel in default_channels:
                    c.execute('''SELECT RoomID FROM rooms WHERE OrgID=? AND ROOM=?''',(OrgID,channel,))
                    RoomID = c.fetchall(); conn.commit()
                    if RoomID: #checks room exists 
                        RoomID = RoomID[0][0]
                        self.create_connection(RoomID,UserID)
                        #creates connection to default channel if they have been created
                    else:
                        pass
                user_list = self.get_org_users(OrgID,UserID)
                #gets all users associated with organisation
                for user in user_list:
                #iterates throughe each user
                    c.execute('''INSERT INTO rooms(ROOM,OrgID,RoomType)
                            VALUES (?,?,?)''',('Private',OrgID,'Private'))
                    #creates new private room for both users
                    last_rid = c.lastrowid
                    #gets last roomID of last row created
                    conn.commit()
                    self.create_connection(last_rid,UserID)
                    #creates connection between room created and current user
                    self.create_connection(last_rid,user['UserID'])
                    #creates connection between room created and user in iteration
                return None #successful
            else:
                return 'Invalid Password'
        else:
            return 'Organisation does not exist'
            
        
# for user in user_list:
            #     if user['UserID'] != UserID:
            #         c.execute('''INSERT INTO rooms(ROOM,OrgID,RoomType) VALUES (?,?,?)''',('Private',OrgID,'Private'))
            #         conn.commit()
            #         c.execute('''SELECT RoomID FROM rooms WHERE ROOM=? AND OrgID=?''',('Private',OrgID,))
            #         RoomID = c.fetchall()[0]; conn.commit()
            #         for room in RoomID:
            #             self.create_connection(room,UserID)
            #             self.create_connection(room,user['UserID']) 
        
    def username_exists(self,username):#
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT EXISTS (SELECT 1 FROM users WHERE USERNAME=?)''',(username,))
        rows = c.fetchall()
        conn.commit()
        conn.close()
        return rows[0][0]
    
    def org_exists(self,orgname):
        #checks if organisation with given orgname exists in database
        conn= sql.connect(self.dbname)
        c=conn.cursor()
        #connects to database
        c.execute('''SELECT EXISTS (SELECT 1 FROM organisation WHERE OrgName=?)''',(orgname,))
        #returns 1 or 0 depending if the OrgName is found in database
        exists = c.fetchall()
        conn.commit()
        conn.close()
        return exists[0][0] #returns 1 or 0

    def get_admin_id(self,OrgID):
        #returns ID of admin user for given organisation
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        #connects to database
        c.execute('''SELECT UserID FROM users WHERE OrgID=? AND RoleID=?''',(OrgID,1,))
        #returns UserID of user with RoleID = 1 = adminstrator
        adminID = c.fetchall()
        conn.commit()
        conn.close()
        return adminID[0][0]#returns ID
        

    def get_user(self,username):#
        conn=sql.connect(self.dbname)
        c=conn.cursor()
        #connects database
        if self.username_exists(username):
            c.execute('''SELECT * FROM users WHERE USERNAME=?''',(username,))
            #selects all fields about user with provided username
            user_data= c.fetchall()
            json_data = self.sql_to_json(c, user_data)#jsonified object
            conn.commit()
            conn.close()
            if self.get_role(json_data[0]['RoleID']) == 'Administrator':
            #if the user is an administrator create an admin instance
                return Admin(json_data[0]['USERNAME'], json_data[0]['PASSWORD'], 
                             json_data[0]['UserID'], json_data[0]['OrgID'], 
                             json_data[0]['StatusID'], json_data[0]['RoleID']) if user_data else None

            #only for non admin users 
            return User(json_data[0]['USERNAME'], json_data[0]['PASSWORD'], 
                        json_data[0]['UserID'], json_data[0]['OrgID'], 
                        json_data[0]['StatusID'], json_data[0]['RoleID']) if user_data else None
        else:
            return None



    def get_status(self,statusID):
        #retrieves status name based on ID
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        #connects to database
        c.execute('''SELECT STATUS FROM status WHERE StatusID=?''',(statusID,))
        #selects the status name based on status ID
        status = c.fetchall()
        conn.commit()
        conn.close()
        return status[0][0] #returns status name
    
    def get_statuses(self):
        #gets all available statuses
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        #connects to database
        c.execute('''SELECT * FROM status''')
        #selects every field and every record from status
        statuses = self.sql_to_json(c,c.fetchall())#jsonified object
        conn.commit()
        conn.close()
        return statuses

    def update_status(self,userID,status):
        #updates status to new status
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        #connects database
        try:
            c.execute('''UPDATE users
                    SET StatusID = ?
                    WHERE UserID = ?'''
                    ,(status,userID,))
            #sets new statusID
            conn.commit()
            conn.close()
            return None
        except:
            return 'Error updating status'
    
    def add_user_to_room(self,userID,roomID):
        #adds a specified user to a specified room
        if self.connection_exists(roomID,userID) == 0: 
        #checks that the user which is to be added is not already connected
            conn = sql.connect(self.dbname) #connects to database
            c = conn.cursor()
            c.execute('''SELECT COUNT(*) FROM connections
                         WHERE RoomID=?''',(roomID,)) 
            #aggregate sql to count number of users in room
            count = c.fetchall()
            if count[0][0] < MAX_USERS: #checks count is less than MAX_USERS
                self.create_connection(roomID,userID)
                #creates connection between room and user
                return None
            else:
                return 'Room Full' #if more than MAX_USERS
        else:
            return 'User is already in this room' #if user already connected
        
        



    def get_role(self,RoleID):
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        #connects to database
        c.execute('''SELECT ROLE FROM roles WHERE RoleID=?''',(RoleID,))
        #selects the name of the role based on the RoleID
        role = c.fetchall()
        conn.commit()
        conn.close()
        return role[0][0]#returns role name

    def get_room_users(self,roomID):
        # gets all users and status of a particular room
        conn=sql.connect(self.dbname) #connects to database
        c = conn.cursor()
        c.execute('''SELECT connections.UserID, users.USERNAME, status.STATUS
                  FROM connections
                  INNER JOIN users
                  ON connections.RoomID = ? AND connections.UserID=users.UserID
                  INNER JOIN status
                  ON users.StatusID = status.StatusID''', (roomID,))
        #selects users and status based on the roomID and statusID
        users_data = self.sql_to_json(c,c.fetchall()) #turns into jsonified object
        conn.commit()
        conn.close() #closes connection
        return users_data
    
    def get_org_users(self,orgID,UserID):
        #gets all users that are members of an organisation
        conn=sql.connect(self.dbname) #connects to database and sets cursor object
        c = conn.cursor()
        c.execute('''SELECT users.UserID, users.USERNAME
                  FROM users
                  WHERE OrgID=? AND UserID!=?''', (orgID,UserID,)) 
        #selects UserID and Username of every user who is part of specified organisation
        users_data = self.sql_to_json(c,c.fetchall()) #turns into jsonified object
        conn.commit()
        conn.close() #closes connection
        return users_data 

    def sql_to_json(self, c, data):#
        row_headers = [x[0] for x in c.description]
        json_data = []
        for result in data:
            json_data.append(dict(zip(row_headers,result)))
        return json_data


    def get_public_room_list(self, userID):
        #returns public rooms associated with user
        conn=sql.connect(self.dbname)
        #connects to database
        c = conn.cursor()
        c.execute('''SELECT rooms.RoomID, rooms.ROOM, rooms.OrgID, RoomType
                      FROM rooms
                      INNER JOIN connections
                      ON connections.UserID=? 
                      AND connections.RoomID=rooms.RoomID
                      AND rooms.RoomType=?''',(userID,"Public",))
        #selects room info for rooms which are public and related to user
        room_data=self.sql_to_json(c,c.fetchall())#jsonified object
        conn.commit()
        conn.close()
        return room_data #returns list
        
        
        
    def get_private_room_list(self, userID):
        #returns list of private rooms
        conn=sql.connect(self.dbname) #connects to database
        c = conn.cursor()
        c.execute('''SELECT rooms.RoomID, rooms.OrgID
                    FROM rooms
                    INNER JOIN connections
                    ON connections.UserID=? 
                    AND connections.RoomID=rooms.RoomID
                    AND rooms.RoomType=?''',(userID,"Private",))
        #selects roomID and orgID of all private rooms for specific user
        room_ids=self.sql_to_json(c,c.fetchall())#jsonified object
        conn.commit()
        private_rooms = [] #assigns empty list
        if room_ids != []: #if roomids is not empty otherwise error is thrown
            for rooms in room_ids:
                c.execute('''SELECT rooms.RoomID, rooms.ROOM, rooms.OrgID, connections.UserID, users.USERNAME
                          FROM rooms
                          INNER JOIN connections
                          ON connections.RoomID = ?
                          AND rooms.RoomID = connections.RoomID
                          AND connections.UserID!=?
                          INNER JOIN users
                          ON users.UserID = connections.UserID
                          ''',(rooms['RoomID'],userID,))
                #selects info about private room based on roomID
                room = self.sql_to_json(c,c.fetchall())#jsonified object
                private_rooms.append(room[0])#appends each room object to private_rooms
        else:
            private_rooms=[] #assigns empty list if room_ids empty
        conn.commit()
        conn.close()
        return private_rooms #returns private_rooms
    
    
    
    
    
    def get_room(self, RoomID, OrgID):
        conn=sql.connect(self.dbname) # creates connection
        c = conn.cursor()
        c.execute('''SELECT rooms.RoomID, rooms.ROOM, rooms.OrgID, rooms.RoomType, organisation.OrgName
                      FROM rooms
                      INNER JOIN organisation
                      ON rooms.RoomID = ? AND organisation.OrgID = ?''',(RoomID,OrgID,))
        #selects all data about specified room
        room_data=self.sql_to_json(c,c.fetchall()) #returns jsonified object
        conn.commit()
        conn.close() #closes connection
        return room_data[0] #returns first element in array
        
    def get_org_id(self,OrgName):
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        #connect to database
        c.execute('''SELECT OrgID FROM organisation WHERE OrgName=?''',(OrgName,))
        #selects the OrgID from a given OrgName
        OrgID = c.fetchall()
        conn.close()
        conn.close()
        return OrgID[0][0] #returns OrgID
    
    def get_org_info(self,OrgID):
        conn = sql.connect(self.dbname) #creates connection
        c = conn.cursor()
        c.execute('''SELECT * FROM organisation WHERE OrgID=?''',(OrgID,))
        #selects all data about a specific organisation
        Org_data = self.sql_to_json(c,c.fetchall()) #turns into jsonified object
        conn.commit()
        conn.close() # closes connection
        if Org_data: # if the returned data is not empty return the first element of the list
            return Org_data[0] 
        else: 
            return [] #if data is empty return an empty list
        
            
    

    def get_connection(self,roomID, username):#
        conn=sql.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT UserID FROM users WHERE USERNAME=?''',(username,))
        userID = c.fetchall()
        userID = userID[0][0]
        c.execute('''SELECT ConnectionID FROM connections WHERE RoomID=? AND UserID=?''',(roomID,userID,))
        client = c.fetchall()
        conn.commit()
        conn.close()
        return client[0][0]

    def save_message(self,username,room_id,message,date,time):#
        conn=sql.connect(self.dbname)
        c = conn.cursor()
        connection_id = self.get_connection(room_id,username)
        c.execute('''INSERT INTO messages(MESSAGE,ConnectionID, Date, Time) VALUES (?,?,?,?)''',(message,connection_id,date,time))
        conn.commit()
        conn.close()

    def get_messages(self,roomID):#
        conn=sql.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT ConnectionID FROM connections WHERE RoomID=?''',(roomID,))
        connections = c.fetchall()
        messages = []
        for i in connections:
            c.execute('''SELECT messages.MessageID, messages.Message, messages.Date, messages.Time, connections.UserID, connections.RoomID, users.USERNAME, rooms.ROOM 
            FROM messages 
            INNER JOIN connections 
            ON messages.ConnectionID=? AND connections.ConnectionID=? 
            INNER JOIN users 
            ON connections.UserID=users.UserID AND connections.ConnectionID=?
            INNER JOIN rooms
            ON rooms.RoomID = connections.RoomID''', 
            (i[0],i[0],i[0],))
            message = c.fetchall()
            if message:
                for j in range(0,len(message)):
                    messages.append(message[j])
            else:
                pass
        json_data = self.sql_to_json(c,messages)
        conn.commit()
        conn.close()
        return json_data
        



    

if __name__ == '__main__':
    run = db('chat')