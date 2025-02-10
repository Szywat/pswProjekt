from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins="*")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
#region baza danych     
#region User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")

with app.app_context():
    db.create_all()
#endregion
#region Ciasteczka
class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(80), unique=True, nullable=False)
    user = db.Column(db.String(80), unique=True, nullable=False)
#endregion
#endregion

PRODUCTS_FILE = "products.txt"
ORDERS_FILE = "orders.json"


def load_products():
    with open(PRODUCTS_FILE, "r") as file:
        try:
            data = json.load(file)
            return data.get("products", [])
        except json.JSONDecodeError:
            return []

def save_products(products):
    with open(PRODUCTS_FILE, "w") as file:
        json.dump({"products": products}, file, indent=4)

def load_orders():
    with open(ORDERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"orders": []}
        
def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)

#region sockets
@socketio.on("login")
def login(username):
    print(f"Użytkownik {username} zalogował się")

@socketio.on("logout")
def logout(username):
    print(f"Użytkownik {username} wylogował się")
#endregion

#region login+register
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    login = data.get("login")
    password = data.get("password")
    user = User.query.filter_by(login=login).first()
    hashed_password = generate_password_hash(password)
    if user and check_password_hash(user.password, password):
        session_id = uuid.uuid4()
        new_session = Sessions(session_id=session_id, user=user)
        db.session.add(new_session)
        db.session.commit()
        response = make_response(jsonify({"success": True, "role": user.role, "username": login, "password": hashed_password}), 200)
        response.set_cookie("session_id", session_id, samesite="Strict")
        return response
    return jsonify({"success": False, "message": "Złe dane do logowania"}), 400

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return jsonify({"success": False, "message": "Brak loginu lub hasła"}), 400
    
    if User.query.filter_by(login=login).first():
        return jsonify({"success": False, "message": "Login jest już zajęty"}), 400
    
    
    hashed_password = generate_password_hash(password)
    new_user = User(login=login,password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "message": "Rejestracja udana. Proszę się zalogować"}), 201

@app.route("/check-login", methods=['GET'])
def check_login():
    session_id = request.cookies.get("session_id")

    session = Sessions.query.filter_by(session_id=session_id).first()
    if session:
        return jsonify({"logged_in": True, "username": session.user})
    return jsonify({"logged_in": False})

@app.route("/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"success": True, "message": "Wylogowano"}))
    response.set_cookie("session_id", "", max_age=0)  # Usunięcie ciasteczka
    return response
#endregion


@app.route("/order/products", methods=["GET"])
def get_products():
    products = load_products()
    return jsonify({"products": products})

@app.route("/order/products", methods=["PATCH"])
def update_products():
    data = request.json
    product_name = data.get("product")
    new_count = data.get("count")

    if product_name is None or new_count is None:
        return jsonify({"success": False, "message": "Brak danych"}), 400
    
    products = load_products()
    for product in products:
        if product["product"] == product_name:
            product["count"] = new_count
            save_products(products)
            return jsonify({"success": True, "message": "Zaktualizowano produkt"}), 200

    return jsonify({"success": False, "message": "Produkt nie istnieje"}), 404

@app.route("/order/user/<username>", methods=["GET"])
def get_user_orders(username):
    orders = load_orders()
    user_orders = [order for order in orders["orders"] if order["user"] == username]
    
    return jsonify({"orders": user_orders})

@app.route("/order/user/<username>", methods=["POST"])
def add_order(username):
    data = request.json
    order_items = data.get("items")

    if not order_items:
        return jsonify({"success": False, "message": "Brak produktów w zamówieniu"}), 400

    orders = load_orders()
    orders["orders"].append({"user": username, "items": order_items})
    save_orders(orders)

    return jsonify({"success": True, "message": "Zamówienie zapisane"}), 201


#region Admin
@app.route("/order/orders", methods=["GET"])
def get_all_orders():
    orders = load_orders()
    return jsonify(orders["orders"])

@app.route("/order/orders", methods=["DELETE"])
def delete_order():
    data = request.json
    index = data.get("index")

    if index is None:
        return jsonify({"success": False, "message": "Brak indeksu zamówienia"}), 400

    orders = load_orders()

    if index < 0 or index >= len(orders["orders"]):
        return jsonify({"success": False, "message": "Nieprawidłowy indeks"}), 400

    del orders["orders"][index]

    save_orders(orders)

    return jsonify({"success": True, "message": "Zamówienie usunięte"}), 200

#endregion

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
