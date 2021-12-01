import hashlib
from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, join_room
from flask_login import LoginManager, login_user, current_user
from sql import db
import secrets
from datetime import datetime
from encryption import encrypt, decrypt
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
        user = load_user(username)
        if user and user.check_password(password):
            print(user.__dict__)
            login_user(user,remember=True)
            session['user'] = {
                "user_id" : user.userID,
                "username" : user.username,
                "org_id" : user.orgID,
                "user_role" : user.permission,
                "statusID" : db.get_status(user.statusID)
            }
            '''ADD STATUS AND ROLE TO SESSION'''
            '''CREATE ADMIN CLASS IN USER.PY - DELETE FUNCTIONALITY, ADDED TO EVERY PUBLIC ROOM'''
            print(current_user.is_authenticated)
            session.modified = True
            return redirect(url_for('show_user',username=session['user']['username'], msg=''))
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
                "statusID" : db.get_status(user.statusID)
            }
            session.modified = True
            return redirect(url_for('show_user',username=session['user']['username']),msg='')
        else:
            return render_template('signup.html',message=message)
    return render_template('signup.html', message='')


@app.route('/<username>',methods=['GET','POST'])
def show_user(username, msg=''):
    print('SESSION LIST',session['user'])
    print('Current User', current_user.is_active)
    if request.method =='POST':
        form_name = request.form.get('name')
        if form_name == 'create_org_form':
            org_name = request.form.get('orgname')
            org_psw = request.form.get('orgpass')
            create_channels = Checked_query[request.form.get('CreateChannels')]
            msg = db.create_org(org_name,org_psw,create_channels,session['user']['user_id'])
            if not msg:
                session['user']['org_id'] = db.get_org_id(org_name)
                session.modified = True
                msg=''
        elif form_name == 'join_org_form':
            org_name = request.form.get('orgname')
            org_psw = request.form.get('orgpass')
            msg = db.join_org(org_name,org_psw,session['user']['user_id'])
            if not msg:
                session['user']['org_id'] = db.get_org_id(org_name)
                session.modified = True
                print('SESSION LIST',session['user'])
                msg=''
        '''1.   elif form is add room
           2.   elif form is change status
           3.   #OPTIONAL# DELETE ROOM FUNCTION AS ADMIN'''
        return redirect(url_for('show_user', username=session['user']['username'], msg=msg))
    organisation_data=db.get_org_info(session['user']['org_id'])
    public_channel_data = get_public_rooms()
    private_channel_data = get_private_rooms()
    return render_template('HomePage.html',
                           organisations=organisation_data,
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
    rid = room_id
    '''CREATE ADD USER BUTTON
        #OPTIONAL# HOVER ON USER FUNCTIONALITY'''
    room_data = get_room_data(rid)
    messages = get_message_history(rid)
    current_date = get_date()
    users_data = get_users_data(rid)
    return render_template('chat.html', 
                            room_data=room_data, 
                            users_data=users_data, 
                            message_history=messages,
                            current_date=str(current_date))

def get_room_data(rid):
    room_data = db.get_room(rid,session['user']['org_id'])
    print(room_data)
    return room_data[0]

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
        message['MESSAGE'] = decrypt(hashlib.sha256(message['ROOM'].encode()).digest(),message['MESSAGE'])
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
    data['message'] = encrypt(hashlib.sha256(data['room'].encode()).digest(),data['message'])
    db.save_message(data['username'],data['roomID'],data['message'],data['date'],data['time'])
    data['message'] = decrypt(hashlib.sha256(data['room'].encode()).digest(),data['message'])
    socketio.emit('recieve_message', data)


if __name__=='__main__':
    socketio.run(app,debug=True)

