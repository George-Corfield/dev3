import sqlite3 as sql
import hashlib
from user import User
import json

default_channels = ['#General','#Work','#Reminders']

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
        h = hashlib.sha256(bytes(password.encode()))
        password = h.hexdigest()
        conn=sql.connect(self.dbname)
        c=conn.cursor()
        if self.username_exists(username) == 0:
            c.execute('''INSERT INTO users(EMAIL,USERNAME,PASSWORD,OrgID) VALUES (?,?,?,?)''', (email,username,password,0))
            conn.commit()
        else:
            return 'Username already exists'
        conn.close()
        return None
    
    def create_org(self,org_name,org_pass,create_channels,userID):
        h = hashlib.sha256(bytes(org_pass.encode()))
        org_pass = h.hexdigest()
        conn=sql.connect(self.dbname)
        c=conn.cursor()
        if self.org_exists(org_name) == 0:
            c.execute('''INSERT INTO organisation(OrgPass,OrgName) VALUES (?,?)''', (org_pass,org_name,))
            conn.commit()
            c.execute('''SELECT OrgID FROM organisation WHERE OrgName=?''',(org_name,))
            OrgID=c.fetchall()
            conn.commit()
            if create_channels:
                for channel in default_channels:
                    c.execute('''INSERT INTO rooms(ROOM,OrgID,RoomType) VALUES (?,?,?)''',(channel,OrgID[0][0],'Public'))
                    conn.commit()
                    c.execute('''SELECT RoomID FROM rooms WHERE ROOM=? AND OrgID=?''',(channel,OrgID[0][0],))
                    RoomID = c.fetchall()
                    conn.commit()
                    self.create_connection(RoomID[0][0],userID)
            c.execute('''UPDATE users SET OrgID=? WHERE UserID=?''',(OrgID[0][0],userID))
            conn.commit()
            conn.close()
        else:
            return 'Organisation Already Exists'
        return None
    
    def create_connection(self,RoomID,UserID):
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        c.execute('''INSERT INTO connections(RoomID,UserID) VALUES (?,?)''',(RoomID,UserID,))
        conn.commit()
        conn.close()
        
    def join_org(self,orgName, orgPass, UserID):
        conn=sql.connect(self.dbname)
        c = conn.cursor()
        if self.org_exists(orgName) == 1:
            OrgID = self.get_org_id(orgName)
            c.execute('''SELECT OrgPass FROM organisation WHERE OrgID = ?''', (OrgID,))
            ExpectedOrgPass = c.fetchall()[0][0]; conn.commit()
            orgpass = hashlib.sha256(bytes(orgPass.encode())).hexdigest()
            if hashlib.sha256(bytes(orgPass.encode())).hexdigest() != ExpectedOrgPass:
                return 'Invalid Password'
            c.execute('''UPDATE users SET OrgID=? WHERE UserID=?''',(OrgID,UserID,))
            conn.commit()
            for channel in default_channels:
                c.execute('''SELECT RoomID FROM rooms WHERE OrgID=? AND ROOM=?''',(OrgID,channel,))
                RoomID = c.fetchall()[0][0]; conn.commit()
                self.create_connection(RoomID,UserID)
        else:
            return 'Organisation does not exist'
        return None
            
        
        
    def username_exists(self,username):
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT EXISTS (SELECT 1 FROM users WHERE USERNAME=?)''',(username,))
        rows = c.fetchall()
        conn.commit()
        conn.close()
        return rows[0][0]
    
    def org_exists(self,orgname):
        conn= sql.connect(self.dbname)
        c=conn.cursor()
        c.execute('''SELECT EXISTS (SELECT 1 FROM organisation WHERE OrgName=?)''',(orgname,))
        exists = c.fetchall()
        conn.commit()
        conn.close()
        return exists[0][0]


    def get_user(self,username):
        conn=sql.connect(self.dbname)
        c=conn.cursor()
        c.execute('''SELECT * FROM users WHERE USERNAME=?''',(username,))
        user_data= c.fetchall()
        json_data = self.sql_to_json(c, user_data)
        conn.commit()
        conn.close()
        return User(json_data[0]['USERNAME'], json_data[0]['PASSWORD'], json_data[0]['UserID'], json_data[0]['OrgID']) if user_data else None
    
    def get_room_users(self,roomID):
        conn=sql.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT connections.UserID, users.USERNAME 
                  FROM connections
                  INNER JOIN users
                  ON connections.RoomID = ? AND connections.UserID=users.UserID''', (roomID,))
        users_data = self.sql_to_json(c,c.fetchall())
        conn.commit()
        conn.close()
        return users_data
    
    def get_org_users(self,orgID):
        conn=sql.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT users.UserID, users.USERNAME
                  FROM users
                  WHERE OrgID=?''', (orgID,))
        users_data = self.sql_to_json(c,c.fetchall())
        conn.commit()
        conn.close()
        return users_data

    def sql_to_json(self, c, data):
        row_headers = [x[0] for x in c.description]
        json_data = []
        for result in data:
            json_data.append(dict(zip(row_headers,result)))
        return json_data


    def get_room_list(self, userID):
        conn=sql.connect(self.dbname)
        c = conn.cursor()
        try:
            c.execute('''SELECT rooms.RoomID, rooms.ROOM, rooms.OrgID, RoomType
                      FROM rooms
                      INNER JOIN connections
                      ON connections.UserID=? 
                      AND connections.RoomID=rooms.RoomID''',(userID,))
            room_data=self.sql_to_json(c,c.fetchall())
        except:
            room_data=[]
        finally:
            conn.commit()
            conn.close()
            return room_data
    
    def get_room(self, RoomID, OrgID):
        conn=sql.connect(self.dbname)
        c = conn.cursor()
        #try:
        c.execute('''SELECT rooms.RoomID, rooms.ROOM, rooms.OrgID, rooms.RoomType, organisation.OrgName
                      FROM rooms
                      INNER JOIN organisation
                      ON rooms.RoomID = ? AND organisation.OrgID = ?''',(RoomID,OrgID,))
        room_data=self.sql_to_json(c,c.fetchall())
        # except:
        #     room_data=[]
        # finally:
        conn.commit()
        conn.close()
        return room_data
        
    def get_org_id(self,OrgName):
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT OrgID FROM organisation WHERE OrgName=?''',(OrgName,))
        OrgID = c.fetchall()
        conn.close()
        conn.close()
        return OrgID[0][0]
    
    def get_org_info(self,OrgID):
        conn = sql.connect(self.dbname)
        c = conn.cursor()
        c.execute('''SELECT * FROM organisation WHERE OrgID=?''',(OrgID,))
        Org_data = self.sql_to_json(c,c.fetchall())
        conn.commit()
        conn.close()
        return Org_data
        
            
    

    def get_client(self,roomID, username):
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

    def save_message(self,username,room_id,message,date,time):
        conn=sql.connect(self.dbname)
        c = conn.cursor()
        connection_id = self.get_client(room_id,username)
        c.execute('''INSERT INTO messages(MESSAGE,ConnectionID, Date, Time) VALUES (?,?,?,?)''',(message,connection_id,date,time))
        conn.commit()
        conn.close()

    def get_messages(self,roomID):
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
    print(run.get_messages(1))