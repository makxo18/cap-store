from app import db, login_manager
from flask_login import UserMixin


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)   # vendor or customer

    # relationship to products
    products = db.relationship('Product', backref='vendor', lazy=True)


class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    price = db.Column(db.Float, nullable=False)

    description = db.Column(db.Text)

    image = db.Column(db.String(200))   # NEW FIELD

    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Cart(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    product_id = db.Column(db.Integer, nullable=False)


# VERY IMPORTANT: required for Flask-Login
@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))