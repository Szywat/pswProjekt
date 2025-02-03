from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

USERS_FILE = "users.txt"
ADMIN_FILE = "admin.txt"

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)

def load_admin():
    if not os.path.exists(ADMIN_FILE):
        return None
    with open(ADMIN_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return None

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    login = data.get("login")
    password = data.get("password")
    if not login or not password:
        return jsonify({"success": False, "message": "Brak loginu lub hasła"}), 400
    
    admin = load_admin()
    if admin and admin["login"] == login and admin["password"] == password:
        return jsonify({"success": True, "message": "Zalogowano", "role": "administrator"}), 200
    
    users = load_users()
    if any(user["login"] == login and user["password"] == password for user in users):
        return jsonify({"success": True, "message": "Zalogowano"}), 201
    
    return jsonify({"success": False, "message": "Błędny login lub hasło"}), 400

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    login = data.get("login")
    password = data.get("password")
    if not login or not password:
        return jsonify({"success": False, "message": "Brak loginu lub hasła"}), 400
    
    users = load_users()
    admin = load_admin()
    if any(user["login"] == login for user in users) or admin["login"] == login:
        return jsonify({"success": False, "message": "Login jest już zajęty"}), 400
    
    users.append({"login": login, "password": password, "role": "user"})
    save_users(users)
    
    return jsonify({"success": True, "message": "Rejestracja udana. Proszę się zalogować"}), 201


if __name__ == "__main__":
    app.run(debug=True)
