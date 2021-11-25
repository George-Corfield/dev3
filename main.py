import hashlib
from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, join_room
from flask_login import LoginManager, login_user, current_user
from sql import db
import secrets
from datetime import datetime
from encryption import encrypt, decrypt

<<<<<<< HEAD
#testing 1
=======
>>>>>>> 0dfe1fb4b9892039a308453685eb4fe49036514f
app = Flask(__name__)
app.secret_key='Z1Uay8j78XHKaltcT0cQFQ'
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)
db = db('chat')
Checked_query = {'on':True,
                 'off':False}


@app.route('/', methods=['POST','GET'])
def login():
    message = ''
    if current_user.is_authenticated:
        return(redirect(url_for('show_user')))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.get_user(username)
        if user and user.check_password(password):
            login_user(user)
            session['user'] = {
                "user_id" : user.userID,
                "username" : user.username,
                "org_id" : user.orgID
            }
            session.modified = True
            return redirect(url_for('show_user',username=session['user']['username']))
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
                "org_id" : user.orgID
            }
            session.modified = True
            return redirect(url_for('show_user',username=session['user']['username']))
        else:
            return render_template('signup.html',message=message)
    return render_template('signup.html', message='')

'''@app.route('/<orgname>', methods=['GET','POST'])
def list_room(orgname):
    room_data = []
    room_list = db.get_room_list(session['user']['user_id'])
    for i in room_list:
        room_data.append(
            {
                "room":'test',
                'room_id':i[0]
            }
        )
    return render_template('Room.html', room_data=room_data)'''

@app.route('/<username>',methods=['GET','POST'])
def show_user(username):
    message = ''
    print('SESSION LIST',session['user'])
    if request.method =='POST':
        form_name = request.form.get('name')
        if form_name == 'create_org_form':
            org_name = request.form.get('orgname')
            org_psw = request.form.get('orgpass')
            create_channels = Checked_query[request.form.get('CreateChannels')]
            message = db.create_org(org_name,org_psw,create_channels,session['user']['user_id'])
            if not message:
                session['user']['org_id'] = db.get_org_id(org_name)
                session.modified = True
                message=''
        elif form_name == 'join_org_form':
            org_name = request.form.get('orgname')
            org_psw = request.form.get('orgpass')
            message = db.join_org(org_name,org_psw,session['user']['user_id'])
            print(message)
            if not message:
                session['user']['org_id'] = db.get_org_id(org_name)
                session.modified = True
                print('SESSION LIST',session['user'])
                message=''
    organisation_data=db.get_org_info(session['user']['org_id'])
    channel_data = get_rooms()
    return render_template('HomePage.html',organisations=organisation_data,
                           channel_data=channel_data,
                           message = message)
    
def get_rooms():
    room_list = db.get_room_list(session['user']['user_id'])
    return room_list
    
    

'''@app.route('/<username>', methods=['GET','POST'])
def list_room(username):
    print(session['user'])
    room_data = []
    room_list = db.get_room_list(session['user']['user_id'])
    for i in room_list:
        room_data.append(
            {
                "room":'test',
                'room_id':i[0]
            }
        )
    return render_template('Room.html', room_data=room_data)'''



@app.route('/chat/<room_id>', methods=['GET','POST'])
def chat(room_id):
    rid = room_id
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
    return db.get_user(username)


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

