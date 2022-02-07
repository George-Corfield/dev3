from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, join_room
from sql import db
import secrets
from datetime import datetime
from encryption import encrypt, decrypt, Hashing_algorithm
from user import User


#testing 1
app = Flask(__name__)
app.secret_key='Z1Uay8j78XHKaltcT0cQFQ'
socketio = SocketIO(app)



db = db('chat')
Checked_query = {'on':True,
                 None:False}

# @app.before_first_request
# def create_tunnel():
#     tunnel = ngrok.connect(5000)
#     print(tunnel)


@app.route('/', methods=['POST','GET'])
def login():
    if not session.get('user'):
        session['user'] = {
                "user_id" : None,
                "username" :None,
                "org_id" : None,
                "user_role" : None,
                "status" : None,
                "is_authenticated": False,
                "is_active": False
        }
    message = ''
    if session['user']['is_authenticated']:
        return redirect(url_for('show_user',username=session['user']['username']))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.retrieve_user(username)
        if user and user.validate(password):
            session['user'] = {
                "user_id" : user.userID,
                "username" : user.username,
                "org_id" : user.orgID,
                "user_role" : db.get_role(user.permission), #returns role name from role id
                "status" : db.get_status(user.statusID), #returns status name from status id
                "is_authenticated": user.is_authenticated(), #returns True
                "is_active": user.is_active(), #returns True
                "is_admin" : user.is_admin() #returns True or False based on Role
            }
            if session['user']['status'] == 'Offline':
                msg = db.update_status(session['user']['status'],3) #3 = 'Online'
                session['user']['status'] = db.get_status(3) #returns 'Online'
            session.modified = True #commits session changes
            return redirect(url_for('show_user',username=session['user']['username']))
        else:
            message = 'Invalid Login Credentials'
    return render_template('login.html',message=message)

'''CREATE ADMIN CLASS IN USER.PY - DELETE FUNCTIONALITY, ADDED TO EVERY PUBLIC ROOM'''

@app.route('/signup', methods=['POST','GET']) #new route for creating accounts
def register():


    if session.get('user') and session['user']['is_authenticated']:
        return redirect(url_for('show_user',username=session['user']['username'],message=''))


    if request.method == 'POST': #checks request methed
        username = request.form.get('username') #gets the username, email and password from form
        password = request.form.get('password')
        email = request.form.get('email')
        message = db.save_user(username,password,email) #calls save user method in sql.py
        
        
        if not message:
            user = db.retrieve_user(username) #gets recently created user
            session['user']={ #sets session data
                "user_id" : user.userID,
                "username" : user.username,
                "org_id" : user.orgID,
                "user_role" : db.get_role(user.permission),#returns role based on roleID
                "status" : db.get_status(user.statusID),#returns status based on status ID
                "is_authenticated": user.is_authenticated(),#returns True
                "is_active": user.is_active(),#returns True
                "is_admin" : user.is_admin()#returns False as no signed up user is admin to start
            }            
            session.modified = True #commits session data
            return redirect(url_for('show_user',username=session['user']['username']))#redirects to homepage
        else:
            return render_template('signup.html',message=message)#rerenders template for signup
    return render_template('signup.html', message='')#renders template with an empty message




@app.route('/<username>',methods=['GET','POST','PUT'])
def show_user(username):
    print(session.get('user'))

    if not session.get('user') or not session['user']['is_authenticated']:
        return redirect(url_for('login'))


    if not session.get('message') or session['message'] =='Room Full' or session['message']=='User is already in this room': #attempts to get the 'message' item from session
        session['message'] = '' #if it doesn't exist it sets it to blank


    if request.method =='POST': #chekcs if data is being submitted via form
        form_name = request.form.get('name') #gets name which is stored in hidden field

        
        if form_name == 'create_org_form': #form for creating a new organisation
            org_name = request.form.get('orgname') #gets name of org from field
            org_psw = request.form.get('orgpass')#gets password of org from field
            create_channels = Checked_query[request.form.get('CreateChannels')] #gets boolean value based on check box
            session['message'] = db.create_org(org_name,org_psw,create_channels,session['user']['user_id'])
            if not session['message']: #if theres no value in message, the creation was successful
                session['user']['user_role'] = db.get_role(1) #changes role to administrator
                session['user']['org_id'] = db.get_org_id(org_name) #changes org id to id of new org
                session['user']['is_admin'] = True #sets admin permissions to true
                session.modified = True #commits session
                session['message'] = '' #sets message to blank value

        elif form_name == 'join_org_form': #form for joining existing org
            org_name = request.form.get('orgname') #name of org from field
            org_psw = request.form.get('orgpass') #password of org from field
            session['message'] = db.join_org(org_name,org_psw,session['user']['user_id']) #returns error message
            if not session['message']: #if there is no error then organisation is successfully joined
                session['user']['user_role'] = db.get_role(2) #makes user have user_role 'User'
                session['user']['org_id'] = db.get_org_id(org_name) #changes orgID from 0 to new orgID
                session['message']='' #sets message to blank
                session.modified = True #commits changes
                

        elif form_name == 'update_status_form': #form for updating status
            status_to_change = request.form.get('status') #ID of requested status change
            session['message'] = db.update_status(session['user']['user_id'], status_to_change) #returns error message
            if not session['message']: #if there is no error then status successfully updated in database
                session['user']['status'] = db.get_status(status_to_change) 
                session['message']=''
                session.modified = True

        elif form_name == 'create_room_form':
            room_name = request.form.get('roomname') #gets name of room to be created

            session['message'] = db.create_room(room_name,session['user']['user_id'],session['user']['org_id'])#returns error message
            if not session['message']: #if there was no error 
                session['message'] = '' #sets message to blank rather than None value
                session.modified = True #commits changes
        
        return redirect(url_for('show_user',username=session['user']['username']))
        '''3.   #OPTIONAL# DELETE ROOM FUNCTION AS ADMIN'''
    
    organisation_data=db.get_org_info(session['user']['org_id'])#returns all information about an organisation

    status_data = db.get_statuses()

    public_channel_data = get_public_rooms() #returns public rooms
    private_channel_data = get_private_rooms() #returns private rooms
    return render_template('HomePage.html', #changed the name of html file 
                           public_channel_data=public_channel_data,
                           private_channel_data=private_channel_data,
                           organisations=organisation_data,
                           status_info = status_data,)
    
def get_public_rooms():
    room_list = db.get_public_room_list(session['user']['user_id'])# returns only rooms with RoomType = 'Public'
    app.logger.info(room_list) # logged for testing
    return room_list

def get_private_rooms():
    room_list = db.get_private_room_list(session['user']['user_id'])# returns only rooms with RoomType = 'Private'
    app.logger.info(room_list) #logged for testing 
    return room_list
   




@app.route('/chat/<room_id>', methods=['GET','POST'])
def chat(room_id):

    if not session.get('user') or not session['user']['is_authenticated']: # checks user is authorised in session
        return redirect(url_for('login')) #if not authorised redirects them to login page

    if session['message'] == 'Error updating status':
        session['message'] == ''

    if request.method=='POST': #checks request method
        form_name = request.form.get('name') #uses hidden field in form to get the form name
        if form_name == 'add_user_form':
            user_to_add = request.form.get('chosen_user')# returns the user name of the user the current user wants to add
            msg = db.add_user_to_room(user_to_add,room_id) #attmepts to add user to the room
            if not msg:
                msg = ''
            session['message'] = msg
        return redirect(url_for('chat',room_id=room_id))#redirects to the room


    rid = room_id


    org_data = get_org_data() #returns data about organisation + users associated with organistaion
    room_data = get_room_data(rid) # returns data about room such as name and type
    messages = get_message_history(rid) #returns messages associated with room
    current_date = get_date() #gets the current date for front end
    users_data = get_users_data(rid) # returns the users who have access to the room excluding current user
    return render_template('chat.html', 
                            room_data=room_data, 
                            users_data=users_data, 
                            message_history=messages,
                            current_date=str(current_date),
                            org_data=org_data) #all data passed to chat.html to be rendered

def get_room_data(rid):
    room_data = db.get_room(rid,session['user']['org_id'])#returns room data from database
    app.logger.info(room_data)#logs data for testing in log
    return room_data #returns to the chat() function

def get_org_data():
    org_users = db.get_org_users(session['user']['org_id'],session['user']['user_id']) # returns users associated with organisation
    org_info = db.get_org_info(session['user']['org_id']) # returns info about org
    org_info['users'] = org_users # appends org_users to org_info data
    app.logger.info(org_info) # logs data for testing in log
    return org_info

def get_users_data(rid):
    users_data = db.get_room_users(rid)
    print(users_data)
    return users_data

def get_date():
    current_date = datetime.now()
    current_date = current_date.strftime('%d/%m/%Y')
    return current_date

def get_message_history(rid):
    messages = db.get_messages(rid)
    quicksort(messages,0,len(messages)-1)
    for message in messages:
        passw = Hashing_algorithm()
        passw.update(message['ROOM'])
        message['MESSAGE'] = decrypt(str(passw.digest()),message['MESSAGE'])
    return messages

def quicksort(array, start_index, end_index):
    if start_index < end_index:#checks if the start index is lower than end index (i.e. array is not 1 element)
        pivot_point = partition(array,start_index, end_index)#finds a pivot point using partition
        quicksort(array,start_index, pivot_point-1) #calls quicksort for the points with an index lower than the pivot point
        quicksort(array,pivot_point+1, end_index)#calls quicksort for the points with an index higher than the pivot point
        


def partition(array,start_index, end_index):
    pivot = array[end_index] #pivot is set to the final value in the array
    t_pivot = start_index-1 #the temp pivot index is set to start-1
    
    for counter in range(start_index,end_index): #goes through each element
        if array[counter]['Date'] == pivot['Date']: #checks if the dates are hte same
            if array[counter]['Time'] < pivot['Time']: #checks if the time of the pivot is greater than current time
                t_pivot +=1 #increments position of temp pivot index
                array[t_pivot],array[counter] = array[counter],array[t_pivot] #swap temp pivot index and current values
        elif array[counter]['Date'] < pivot['Date']: #checks if date of pivot is greater 
            t_pivot+=1
            array[t_pivot],array[counter] = array[counter],array[t_pivot]
        else:
            pass

    array[t_pivot+1],array[end_index] = array[end_index],array[t_pivot+1] #swaps value at end index (pivot) with temp pivot index
    return (t_pivot+1) #returns temp pivot index



@app.route('/logout') #creates new route called logout
def logout():
    if not session.get('user') or not session['user']['is_authenticated']: #checks firstly user key exists and secondly that they are authenticated
        return redirect(url_for('login')) #if not authenticated returned to login
    db.update_status(session['user']['user_id'],2) #updates status to offline
    session.clear() #clears session data and removes user key
    return redirect(url_for('login')) #redirects to login page








@socketio.on('join_room')
def handle_connect(data,methods=['GET','POST']):
    app.logger.info(f"joined room: {data['room']}")
    join_room(data['room'])
    socketio.emit('joined-room')

@socketio.on('send_message')
def handle_message(data,methods=['POST','GET']):
    passw = Hashing_algorithm()
    passw.update(data['room'])
    data['message'] = encrypt(str(passw.digest()),data['message'])
    db.save_message(data['username'],data['roomID'],data['message'],data['date'],data['time'])
    data['message'] = decrypt(str(passw.digest()),data['message'])
    socketio.emit('recieve_message', data)

if __name__=='__main__':
    socketio.run(app,debug=True)

