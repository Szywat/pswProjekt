from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

USERS_FILE = "users.txt"
ADMIN_FILE = "admin.txt"
PRODUCTS_FILE = "products.txt"
ORDERS_FILE = "orders.json"
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

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    login = data.get("login")
    password = data.get("password")
    if not login or not password:
        return jsonify({"success": False, "message": "Brak loginu lub hasła"}), 400
    
    admin = load_admin()
    if admin and admin["login"] == login and admin["password"] == password:
        return jsonify({"success": True, "message": "Zalogowano", "role": "administrator", "username": login}), 200
    
    users = load_users()
    if any(user["login"] == login and user["password"] == password for user in users):
        return jsonify({"success": True, "message": "Zalogowano", "username": login}), 201
    
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

@app.route("/order/user/<string:username>", methods=["POST"])
def add_order(username):
    data = request.json
    order_items = data.get("items")

    if not order_items:
        return jsonify({"success": False, "message": "Brak produktów w zamówieniu"}), 400

    orders = load_orders()
    orders["orders"].append({"user": username, "items": order_items})
    save_orders(orders)

    return jsonify({"success": True, "message": "Zamówienie zapisane"}), 201

if __name__ == "__main__":
    app.run(debug=True)
