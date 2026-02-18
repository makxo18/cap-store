from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from app.models import User, Product, Cart

routes = Blueprint("routes", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@routes.route("/")
def home():
    return render_template("home.html")

# ---------------- REGISTER ----------------
@routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed_pw = generate_password_hash(request.form["password"])

        new_user = User(
            username=request.form["username"],
            email=request.form["email"],
            password=hashed_pw,
            role=request.form["role"]
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("routes.login"))

    return render_template("register.html")

# ---------------- LOGIN ----------------
@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("routes.dashboard"))

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("routes.home"))

# ---------------- DASHBOARD ----------------
@routes.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# ---------------- ADD PRODUCT (Vendor Only) ----------------
@routes.route("/add-product", methods=["GET", "POST"])
@login_required
def add_product():
    if current_user.role != "vendor":
        return "Access Denied"

    if request.method == "POST":
        product = Product(
            name=request.form["name"],
            price=float(request.form["price"]),
            description=request.form["description"],
            vendor_id=current_user.id
        )

        db.session.add(product)
        db.session.commit()

        return redirect(url_for("routes.vendor_products"))

    return render_template("add_product.html")

# ---------------- VENDOR PRODUCTS ----------------
@routes.route("/vendor-products")
@login_required
def vendor_products():
    if current_user.role != "vendor":
        return "Access Denied"

    products = Product.query.filter_by(vendor_id=current_user.id).all()
    return render_template("vendor_products.html", products=products)

# ---------------- VIEW ALL PRODUCTS ----------------
@routes.route("/products")
def products():
    all_products = Product.query.all()
    return render_template("products.html", products=all_products)

# ---------------- ADD TO CART ----------------
@routes.route("/add-to-cart/<int:product_id>")
@login_required
def add_to_cart(product_id):
    cart_item = Cart(
        user_id=current_user.id,
        product_id=product_id
    )

    db.session.add(cart_item)
    db.session.commit()

    return redirect(url_for("routes.cart"))

# ---------------- VIEW CART ----------------
@routes.route("/cart")
@login_required
def cart():
    items = Cart.query.filter_by(user_id=current_user.id).all()

    products = []
    for item in items:
        product = Product.query.get(item.product_id)
        if product:
            products.append(product)

    return render_template("cart.html", products=products)
