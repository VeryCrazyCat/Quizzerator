
from firebase_admin import auth
from flask import redirect,request,render_template, url_for, session, jsonify

def authenticate():
    if request.json["mode"] == "signup":
        email = request.json["email"]
        password = request.json["password"]
        username = request.json["username"]
        user = auth.create_user(email=email, password=password, display_name=username)
        return jsonify({"message": "User created successfully", "uid": user.uid})
    if request.json["mode"] == "signin":
        userinfo = request.json["userinfo"]
        session["user"] = {
            "email": userinfo["user"]["email"],
            "uid": userinfo["user"]["uid"],
            "display_name": userinfo["user"]["displayName"]
        }
        return jsonify({"message": "success"})
    if request.json["mode"] == "signout":
        session.pop("user", None)
        return jsonify({"message": "success"})
    if request.json["mode"] == "getsessioninfo":
        if "user" in session:
            return session["user"]
        else:
            return {
                "email": "",
                "uid": "",
                "display_name" : "",
            }

#auth.create_user_with_email_and_password(email, password)

#https://www.youtube.com/watch?v=HltzFtn9f1c