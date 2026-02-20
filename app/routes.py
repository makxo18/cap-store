from flask import Blueprint, render_template, redirect, url_for, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from app import db
from app.models import User, Product, Cart


routes = Blueprint("routes", __name__)


# ---------------- HOME ----------------
@routes.route("/")
def home():
    return render_template("home.html")


# ---------------- REGISTER ----------------
@routes.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        existing_user = User.query.filter_by(
            email=request.form["email"]
        ).first()

        if existing_user:
            return redirect(url_for("routes.login"))

        hashed_pw = generate_password_hash(
            request.form["password"]
        )

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

        user = User.query.filter_by(
            email=request.form["email"]
        ).first()

        if user and check_password_hash(
            user.password,
            request.form["password"]
        ):

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


# ---------------- VIEW ALL PRODUCTS ----------------
@routes.route("/products")
@login_required
def products():

    all_products = Product.query.all()

    return render_template(
        "products.html",
        products=all_products
    )


# ---------------- ADD PRODUCT (Vendor Only) ----------------
@routes.route("/add-product", methods=["GET", "POST"])
@login_required
def add_product():

    if current_user.role != "vendor":
        return redirect(url_for("routes.dashboard"))

    if request.method == "POST":

        image_file = request.files["image"]

        filename = None

        if image_file and image_file.filename != "":

            filename = secure_filename(image_file.filename)

            upload_folder = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "static",
                "uploads"
            )

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            image_path = os.path.join(upload_folder, filename)

            image_file.save(image_path)

        product = Product(
            name=request.form["name"],
            price=float(request.form["price"]),
            description=request.form["description"],
            image=filename,
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
        return redirect(url_for("routes.dashboard"))

    products = Product.query.filter_by(
        vendor_id=current_user.id
    ).all()

    return render_template(
        "vendor_products.html",
        products=products
    )


# ---------------- DELETE PRODUCT ----------------
@routes.route("/delete-product/<int:product_id>")
@login_required
def delete_product(product_id):

    product = Product.query.get(product_id)

    if not product:
        return redirect(url_for("routes.vendor_products"))

    # only vendor who owns product can delete
    if product.vendor_id != current_user.id:
        return redirect(url_for("routes.dashboard"))

    # delete image file
    if product.image:
        image_path = os.path.join(
            current_app.static_folder,
            "uploads",
            product.image
        )

        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(product)
    db.session.commit()

    return redirect(url_for("routes.vendor_products"))


# ---------------- ADD TO CART ----------------
@routes.route("/add-to-cart/<int:product_id>")
@login_required
def add_to_cart(product_id):

    product = Product.query.get(product_id)

    if not product:
        return redirect(url_for("routes.products"))

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

    items = Cart.query.filter_by(
        user_id=current_user.id
    ).all()

    products = []

    for item in items:

        product = Product.query.get(item.product_id)

        if product:
            products.append(product)

    return render_template(
        "cart.html",
        products=products
    )


# ---------------- REMOVE FROM CART ----------------
@routes.route("/remove-from-cart/<int:product_id>")
@login_required
def remove_from_cart(product_id):

    cart_item = Cart.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:

        db.session.delete(cart_item)
        db.session.commit()

    return redirect(url_for("routes.cart"))