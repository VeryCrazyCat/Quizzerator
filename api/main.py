#!/usr/bin/python
# run.py

from flask import Flask, render_template,request, redirect
import routes.quiz as quiz
import routes.uploader as uploader
import routes.quiz_master as quiz_master
import routes.index as index
import routes.quiz_searcher as quiz_searcher
import routes.authenticator as authenticator
import routes.login_page as login_page
import routes.live_quiz as live_quiz
import scheduler_tasks.clear_database as clear_database
import firebase_db as firebase_db
from apscheduler.schedulers.background import BackgroundScheduler
from flask_socketio import SocketIO, emit, send, join_room, leave_room, rooms

import subprocess
from flask import session
import uuid


firebase_db.setup()

app = Flask(__name__)
app.secret_key = "6BtdCaEka6xjV4DVNxZ3pZB8mXJ70sig"
scheduler = BackgroundScheduler()
socketio = SocketIO(app,debug=True,cors_allowed_origins='*')


@app.route('/', endpoint="index", methods=["GET", "POST"])
def index_():
    return index.load_index()

@app.route("/uploader", methods = ["GET", "POST"])
def upload_file():
    return uploader.uploader()

@app.route("/quiz", methods=["POST"])
def gen_quiz():
    return quiz.generate_quiz()

@app.route("/quiz_master", methods=["GET", "POST"])
def mark_question():
    return quiz_master.mark_question()

@app.route("/quiz_searcher", methods=["GET", "POST"])
def quiz_search():
    return quiz_searcher.search()

@app.route("/authenticator", methods=["GET", "POST"])
def authenticateuser():
    return authenticator.authenticate()

@app.route("/login", methods=["GET", "POST"])
def loginpage():
    return login_page.display_login_page()

@app.route("/live_quiz", methods=["GET", "POST"])
def live_quiz_connect():
    return live_quiz.live_quiz_connect()



@socketio.on("client_data")
def test_message(data):
    print("Received" + str(data))
    emit('server_data', {'data': "123"})


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)

    session_user = session["user"]["display_name"]
    #print(request.sid)
    #print(dict(socketio.server.manager.rooms["/"]["room123"]).keys()) #THIS GETS ALL SIDS IN ROOM
    new_data = {
        "display_name": session_user,
        "sid": request.sid,
        }
    room_db = firebase_db.download_quiz(room, "liveRooms")
    if room in firebase_db.get_all_keys("liveRooms"):
        current_users = room_db["users"]

        #ERASES all users not in flask-socketio room
        if room in dict(socketio.server.manager.rooms["/"]):
            server_room = dict(socketio.server.manager.rooms["/"][room]).keys()
            for user_num in range(len(current_users)-1, -1, -1):
                user = current_users[user_num]
                if not user["sid"] in server_room:
                    current_users.remove(user)
                if user["sid"] == request.sid:
                    current_users.remove(user)
            current_users.append(new_data)

            firebase_db.update_quiz(room, "users", current_users, "liveRooms")
            all_users = current_users
            #all_users = firebase_db.download_quiz(room, "liveRooms")
            emit("room_data", {"data": all_users}, to=room)
            emit("toast_messages", {"data": session_user + ' has entered the room.'}, to=room)

@socketio.on("get_room_info")
def on_get_info(data):
    room = data["room"]
    all_users = firebase_db.download_quiz(room, "liveRooms")["users"]
    for user_num in range(len(all_users)-1, -1, -1):
        
        user = all_users[user_num]
        server_room = dict(socketio.server.manager.rooms["/"][room]).keys()
        if not user["sid"] in server_room:
            all_users.remove(user)
    firebase_db.update_quiz(room, "users", all_users, "liveRooms")
    emit("room_data", {"data": all_users})
@socketio.on('create')
def on_join(data):
    
    session_user = session["user"]["display_name"]
    new_data = {
        "display_name": session_user,
        "sid": request.sid,
    }
    room_id = str(uuid.uuid1())[:7]
    join_room(room_id)
    firebase_db.upload_quiz(room_id, {"host": new_data, "users": []}, "liveRooms")
    
    #print(socketio.server.manager.rooms["/"]["room123"])
    emit("room_creation_data", {"data": room_id})
    emit("toast_messages", {"data": "Room created"}, to=room_id)
    
@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit("toast_messages", {"data": username + ' has left the room.'}, to=room)

def clear_database_task():
    clear_database.clear()

if __name__ == "__main__":
    
    scheduler.add_job(clear_database_task, 'interval', seconds=15)
    scheduler.start()
    app.run(debug=True, host="0.0.0.0", port=80)