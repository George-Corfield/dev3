from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, join_room
from flask_login import LoginManager, login_user, current_user, logout_user
from sql import db
import secrets
from datetime import datetime
from encryption import encrypt, decrypt, Hashing_algorithm
from user import User

#testing 1
app = Flask(__name__)
app.secret_key='Z1Uay8j78XHKaltcT0cQFQ'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

db = db('chat')
Checked_query = {'on':True,
                 'off':False}


@app.route('/', methods=['POST','GET'])
def login():
    message = ''
    if current_user.is_authenticated:
        return(redirect(url_for('show_user',username=session['user']['username'],msg='')))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.get_user(username)
        if user and user.check_password(password):
            login_user(user,remember=True)
            print(str(current_user))
            session['user'] = {
                "user_id" : user.userID,
                "username" : user.username,
                "org_id" : user.orgID,
                "user_role" : db.get_role(user.permission),
                "status" : db.get_status(user.statusID)
            }
            if session['user']['status'] == 'Offline':
                msg = db.update_status(session['user']['status'],3)
                session['user']['status'] = db.get_status(3)
            '''CREATE ADMIN CLASS IN USER.PY - DELETE FUNCTIONALITY, ADDED TO EVERY PUBLIC ROOM'''
            session.modified = True
            return redirect(url_for('show_user',username=session['user']['username'],))
        else:
            message = 'Invalid Login Credentials'
    return render_template('login.html',message=message)

@app.route('/signup', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        message = db.save_user(username,password,email)
        if not message:
            user = load_user(username)
            session['user']={
                "user_id" : user.userID,
                "username" : user.username,
                "org_id" : user.orgID,
                "user_role" : db.get_role(user.permission),
                "status" : db.get_status(user.statusID)
            }
            session.modified = True
            return redirect(url_for('show_user',username=session['user']['username']))
        else:
            return render_template('signup.html',message=message)
    return render_template('signup.html', message='')


@app.route('/<username>',methods=['GET','POST','PUT'])
def show_user(username, msg=''):
    print('SESSION LIST',session['user'])
    print('Current User', str(current_user))
    if request.method =='POST':
        form_name = request.form.get('name')
        if form_name == 'create_org_form':
            org_name = request.form.get('orgname')
            org_psw = request.form.get('orgpass')
            create_channels = Checked_query[request.form.get('CreateChannels')]
            msg = db.create_org(org_name,org_psw,create_channels,session['user']['user_id'])
            session['user']['user_role'] = db.get_role(1)
            if not msg:
                session['user']['org_id'] = db.get_org_id(org_name)
                session.modified = True
                msg=''
        elif form_name == 'join_org_form':
            org_name = request.form.get('orgname')
            org_psw = request.form.get('orgpass')
            msg = db.join_org(org_name,org_psw,session['user']['user_id'])
            session['user']['user_role'] = db.get_role(2)
            if not msg:
                session['user']['org_id'] = db.get_org_id(org_name)
                session.modified = True
                print('SESSION LIST',session['user'])
                msg=''
        elif form_name == 'update_status_form':
            status_to_change = request.form.get('status')
            msg = db.update_status(session['user']['user_id'], status_to_change)
            if not msg:
                session['user']['status'] = db.get_status(status_to_change)
                session.modified = True
                msg=''
        elif form_name == 'create_room_form':
            room_name = request.form.get('roomname')
            msg = db.create_room(room_name,session['user']['user_id'],session['user']['org_id'])
        '''3.   #OPTIONAL# DELETE ROOM FUNCTION AS ADMIN'''
        return redirect(url_for('show_user', username=session['user']['username'], msg=msg))
    organisation_data=db.get_org_info(session['user']['org_id'])
    status_data = db.get_statuses()
    public_channel_data = get_public_rooms()
    private_channel_data = get_private_rooms()
    return render_template('HomePage.html',
                           organisations=organisation_data,
                           status_info = status_data,
                           public_channel_data=public_channel_data,
                           private_channel_data=private_channel_data,
                           message = msg)
    
def get_public_rooms():
    room_list = db.get_public_room_list(session['user']['user_id'])
    return room_list

def get_private_rooms():
    room_list = db.get_private_room_list(session['user']['user_id'])
    return room_list
   




@app.route('/chat/<room_id>', methods=['GET','POST'])
def chat(room_id):
    if request.method=='POST':
        form_name = request.form.get('name')
        if form_name == 'add_user_form':
            user_to_add = request.form.get('chosen_user')
            msg = db.add_user_to_room(user_to_add,room_id)
        return redirect(url_for('chat',room_id=room_id))
    rid = room_id
        #OPTIONAL# HOVER ON USER FUNCTIONALITY
    org_data = get_org_data()
    room_data = get_room_data(rid)
    messages = get_message_history(rid)
    current_date = get_date()
    users_data = get_users_data(rid)
    return render_template('chat.html', 
                            room_data=room_data, 
                            users_data=users_data, 
                            message_history=messages,
                            current_date=str(current_date),
                            org_data=org_data)

def get_room_data(rid):
    room_data = db.get_room(rid,session['user']['org_id'])
    print(room_data)
    return room_data[0]

def get_org_data():
    org_users = db.get_org_users(session['user']['org_id'],session['user']['user_id'])
    org_info = db.get_org_info(session['user']['org_id'])
    org_info['users'] = org_users
    return org_info

def get_users_data(rid):
    users_data = db.get_room_users(rid)
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
        message['MESSAGE'] = decrypt(passw.digest(),message['MESSAGE'])
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




@login_manager.user_loader
def load_user(username):
    user_data = db.get_user(username)
    if user_data:
        return User(user_data[0],user_data[1],user_data[2],user_data[3],user_data[4],user_data[5])
    return None

'''ADD LOGOUT FUNCTION'''




@socketio.on('join_room')
def handle_connect(data,methods=['GET','POST']):
    app.logger.info(f"joined room: {data['room']}")
    join_room(data['room'])
    socketio.emit('joined-room')

@socketio.on('send_message')
def handle_message(data,methods=['POST','GET']):
    app.logger.info('recieved message')
    passw = Hashing_algorithm()
    passw.update(data['room'])
    data['message'] = encrypt(passw.digest(),data['message'])
    db.save_message(data['username'],data['roomID'],data['message'],data['date'],data['time'])
    data['message'] = decrypt(passw.digest(),data['message'])
    socketio.emit('recieve_message', data)


if __name__=='__main__':
    socketio.run(app,debug=True)

