from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
app.app_context().push()
db = SQLAlchemy(app)
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(id):
    return user_details.query.get(id)


class user_details(db.Model, UserMixin):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.Integer)
    role = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, name, surname, username, email, password, phone, role):
        self.name = name
        self.surname = surname
        self.username = username
        self.email = email
        self.password = password
        self.phone = phone
        self.role = role

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "phone": self.phone,
            "role": self.role,
            "date_created": self.date_created
        }


class items(db.Model):
    item_id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    rate = db.Column(db.String(80), unique=True, nullable=False)
    category = db.Column(db.String(120), unique=True, nullable=False)
    sales = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<Item %r>' % self.name

    def __init__(self, name, rate, category, sales):
        self.name = name
        self.rate = rate
        self.category = category
        self.sales = sales

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "rate": self.rate,
            "category": self.category,
            "sales": self.sales
        }


class invoices(db.Model):
    invoice_id = db.Column(db.String(80), primary_key=True)
    item = db.Column(db.String(80), db.ForeignKey('items.item_id'), nullable=False)
    quantity = db.Column(db.String(80), unique=True, nullable=False)
    total = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(120), unique=True, nullable=False)
    table_no = db.Column(db.String(120), unique=True, nullable=False)
    user = db.Column(db.String(120), db.ForeignKey('user_details.id'), nullable=False)

    def __repr__(self):
        return '<Invoice %r>' % self.id

    def __init__(self, item, quantity, total, date, table_no, user):
        self.item = item
        self.quantity = quantity
        self.total = total
        self.date = date
        self.table_no = table_no
        self.user = user

    def serialize(self):
        return {
            "id": self.id,
            "item": self.item,
            "quantity": self.quantity,
            "total": self.total,
            "date": self.date,
            "table_no": self.table_no,
            "user": self.user
        }


class tables(db.Model):
    table_id = db.Column(db.String(80), primary_key=True)
    status = db.Column(db.String(80), unique=True, nullable=False)
    user = db.Column(db.String(120), db.ForeignKey('user_details.id'), nullable=False)
    order_id = db.Column(db.String(80), db.ForeignKey('orders.order_id'), nullable=False)

    def __repr__(self):
        return '<Table %r>' % self.id

    def __init__(self, status, user):
        self.status = status
        self.user = user

    def serialize(self):
        return {
            "id": self.id,
            "status": self.status,
            "user": self.user
        }


class orders(db.Model):
    order_id = db.Column(db.String(80), primary_key=True)
    item = db.Column(db.String(80), db.ForeignKey('items.item_id'), nullable=False)
    quantity = db.Column(db.String(80), unique=True, nullable=False)
    total = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(120), unique=True, nullable=False)
    table_no = db.Column(db.String(120), unique=True, nullable=False)
    user = db.Column(db.String(120), db.ForeignKey('user_details.id'), nullable=False)

    def __repr__(self):
        return '<Order %r>' % self.id

    def __init__(self, item, quantity, total, date, table_no, user):
        self.item = item
        self.quantity = quantity
        self.total = total
        self.date = date
        self.table_no = table_no
        self.user = user

    def serialize(self):
        return {
            "id": self.id,
            "item": self.item,
            "quantity": self.quantity,
            "total": self.total,
            "date": self.date,
            "table_no": self.table_no,
            "user": self.user
        }


class archives(db.Model):
    invoice_id = db.Column(db.String(80), primary_key=True)
    item = db.Column(db.String(80), db.ForeignKey('items.item_id'), nullable=False)
    quantity = db.Column(db.String(80), unique=True, nullable=False)
    total = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(120), unique=True, nullable=False)
    table_no = db.Column(db.String(120), db.ForeignKey('tables.table_id'), nullable=False)
    user = db.Column(db.String(120), db.ForeignKey('user_details.id'), nullable=False)

    def __repr__(self):
        return '<Archive %r>' % self.id

    def __init__(self, item, quantity, total, date, table_no, user):
        self.item = item
        self.quantity = quantity
        self.total = total
        self.date = date
        self.table_no = table_no
        self.user = user

    def serialize(self):
        return {
            "id": self.id,
            "item": self.item,
            "quantity": self.quantity,
            "total": self.total,
            "date": self.date,
            "table_no": self.table_no,
            "user": self.user
        }


@app.route('/', methods=['GET','POST'])
def login():
    # Login with flask_login
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_details.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('You have successfully logged in')
                return redirect(url_for('authenticate'))
            flash('Incorrect password')
            return redirect(url_for('login'))
        flash('Email does not exist')
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/authenticate', methods=['GET','POST'])
def authenticate():
    if current_user.role == '0':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == '1':
        return redirect(url_for('owner_dashboard'))
    elif current_user.role == '2':
        return redirect(url_for('waiter_dashboard'))
    elif current_user.role == '3':
        return redirect(url_for('chef_dashboard'))


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        args = request.form
        name = args.get('name')
        surname = args.get('surname')
        username = args.get('username')
        email = ""
        password = args.get('password')
        confirm_password = args.get('confirm_password')
        phone = ""
        role = args.get('role')
        if password == confirm_password:
            user = user_details(name, surname, username, email, generate_password_hash(password), phone, role)
            db.session.add(user)
            db.session.commit()
            flash('New user created successfully')
            return redirect(url_for('login'))
        flash('Passwords do not match')
        return render_template('register.html')
    return render_template('register.html')


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out')
    return redirect(url_for('login'))


db.create_all()
if __name__ == '__main__':
    app.run(debug=True)