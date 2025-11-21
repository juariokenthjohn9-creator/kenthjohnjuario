from flask import Flask, render_template, request, redirect, session, url_for, flash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Example inventory
plants = [
    {"id": 1, "name": "Monstera Deliciosa", "price": 500, "img": "Monstera Deliciosa.jpg"},
    {"id": 2, "name": "Fiddle Leaf Fig", "price": 700, "img": "Fiddle Leaf Fig.jpg"},
    {"id": 3, "name": "Snake Plant", "price": 300, "img": "Snake Plant.jpg"}
]

# Simple in-memory user storage
users = {}  # Format: {username: password}

# ===================== HOME =====================
@app.route("/")
def home():
    username = session.get("username")
    return render_template("home.html", plants=plants, username=username)

# ===================== CART ROUTES =====================
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    plant_id = int(request.form.get("plant_id"))
    qty = int(request.form.get("quantity"))

    if "cart" not in session:
        session["cart"] = []

    cart = session["cart"]
    found = False
    for item in cart:
        if item["id"] == plant_id:
            item["qty"] += qty
            found = True
            break

    if not found:
        plant = next((p for p in plants if p["id"] == plant_id), None)
        if plant:
            cart.append({"id": plant["id"], "name": plant["name"], "price": plant["price"], "qty": qty, "img": plant["img"]})

    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    total = sum(item["price"] * item["qty"] for item in cart)
    username = session.get("username")
    return render_template("cart.html", cart=cart, total=total, username=username)

@app.route("/update_cart", methods=["POST"])
def update_cart():
    updates = request.form
    cart = session.get("cart", [])
    for item in cart:
        str_id = str(item["id"])
        if str_id in updates:
            qty = int(updates[str_id])
            item["qty"] = max(qty, 1)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/remove/<int:plant_id>")
def remove_item(plant_id):
    cart = session.get("cart", [])
    cart = [item for item in cart if item["id"] != plant_id]
    session["cart"] = cart
    return redirect(url_for("cart"))

# ===================== CHECKOUT =====================
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "username" not in session:
        flash("Please login first to checkout.")
        return redirect(url_for("login"))

    cart = session.get("cart", [])
    total = sum(item["price"] * item["qty"] for item in cart)
    
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        address = request.form.get("address")
        session.pop("cart", None)
        flash(f"Thank you {name}! Your purchase of ₱{total} has been confirmed.")
        return redirect(url_for("home"))
    
    username = session.get("username")
    return render_template("checkout.html", cart=cart, total=total, username=username)

# ===================== AUTHENTICATION =====================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if not username or not password:
            flash("Please fill in all fields.")
            return redirect(url_for("register"))
        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for("register"))
        if username in users:
            flash("Username already exists.")
            return redirect(url_for("register"))
        users[username] = password
        flash("Registration successful. You can now log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
            session["username"] = username 
            flash(f"Welcome {username}!")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.")
    return redirect(url_for("home"))

if __name__ == "__main__":
    try:
        print("Starting Flask server...")
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Make sure Flask is installed: pip install flask")
