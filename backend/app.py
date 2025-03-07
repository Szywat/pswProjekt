from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
socketio = SocketIO(app, cors_allowed_origins="*")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

rooms = {}

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

@socketio.on("login")
def logout(username):
    print(f"Użytkownik {username} zalogował się")

@socketio.on("logout")
def logout(username):
    print(f"Użytkownik {username} wylogował się")

@socketio.on("join")
def handle_join(data):
    user_id = data["user_id"]
    room = f"chat_{user_id}"
    join_room(room)
    rooms[user_id] = room
    emit("message", {"user": "System", "text": "Połączono z czatem."}, room=room)

@socketio.on("message")
def handle_message(arg1, arg2):

    data = {"login": arg2, "text": arg1}
    emit("message", data, broadcast=True)

#region login+register
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    login = data.get("login")
    password = data.get("password")
    user = User.query.filter_by(login=login).first()
    hashed_password = generate_password_hash(password)
    if user and check_password_hash(user.password, password):
        return jsonify({"success": True, "role": user.role, "username": login, "password": hashed_password}), 200
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

#endregion

#region user
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
#endregion

#region admin
@app.route("/order/orders", methods=["GET"])
def get_all_orders():
    search = request.args.get("search", "").lower()
    orders = load_orders()
    filtered_orders = [
        order for order in orders["orders"]
        if search in order["user"].lower()
    ]
    
    if filtered_orders == [] and search == "":
        return jsonify(orders["orders"])
    return jsonify(filtered_orders)

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
