from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import random, string


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
    item_id = db.Column(db.Integer, unique=True, nullable=False, autoincrement=True, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    rate = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(120))
    sales = db.Column(db.String(120), nullable=False)

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
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    invoice_id = db.Column(db.String(80), nullable=False)
    item = db.Column(db.String(80), db.ForeignKey('items.item_id'), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    total = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    table_no = db.Column(db.String(120), nullable=False)
    user = db.Column(db.String(120), db.ForeignKey('user_details.id'), nullable=False)

    def __repr__(self):
        return '<Invoice %r>' % self.id

    def __init__(self, invoice_id, item, quantity, total, date, table_no, user):
        self.invoice_id = invoice_id
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
    table_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    status = db.Column(db.String(80), nullable=False)
    user = db.Column(db.String(120), db.ForeignKey('user_details.id'))
    order_id = db.Column(db.String(80))

    def __repr__(self):
        return '<Table %r>' % self.table_id

    def __init__(self, name, status, user, order_id):
        self.name = name
        self.status = status
        self.user = user
        self.order_id = order_id

    def serialize(self):
        return {
            "id": self.table_id,
            "name": self.name,
            "status": self.status,
            "user": self.user,
            "order_id": self.order_id
        }


class orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(80))
    item = db.Column(db.String(80), db.ForeignKey('items.item_id'), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    total = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    table_no = db.Column(db.String(120), nullable=False)
    user = db.Column(db.String(120), db.ForeignKey('user_details.id'), nullable=False)

    def __repr__(self):
        return '<Order %r>' % self.id

    def __init__(self, order_id, item, quantity, total, table_no, user):
        self.order_id = order_id
        self.item = item
        self.quantity = quantity
        self.total = total
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
    quantity = db.Column(db.String(80), nullable=False)
    total = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
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

class chef_orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(80))
    order_id = db.Column(db.String(80))
    item = db.Column(db.String(80), db.ForeignKey('items.item_id'), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    table_no = db.Column(db.String(120), nullable=False)
    user = db.Column(db.String(120), db.ForeignKey('user_details.id'), nullable=False)
    sent = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Order %r>' % self.id

    def __init__(self, order_id, item, quantity, table_no, user, sent):
        self.order_id = order_id
        self.request_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        self.item = item
        self.quantity = quantity
        self.table_no = table_no
        self.user = user
        self.sent = sent

    def serialize(self):
        return {
            "id": self.id,
            "item": self.item,
            "quantity": self.quantity,
            "date": self.date,
            "table_no": self.table_no,
            "user": self.user,
            "sent": self.sent
        }

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if current_user.role == '0':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == '1':
        return redirect(url_for('owner_dashboard'))
    elif current_user.role == '2':
        return redirect(url_for('waiter_dashboard'))
    elif current_user.role == '3':
        return redirect(url_for('chef_dashboard'))



@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET','POST'])
def login():
    # Login with flask_login
    if request.method == 'POST':
        username = request.form['username'].lower().strip()
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
    else:
        return redirect(url_for('login'))


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        args = request.form
        name = args.get('name')
        surname = args.get('surname')
        username = args.get('username')
        email = args.get('email')
        password = args.get('password')
        confirm_password = args.get('confirm_password')
        phone = ""
        role = args.get('role')
        user = user_details.query.filter_by(username=username).first()
        try:
            if password == confirm_password and user is None:
                user = user_details(name, surname, username, email, generate_password_hash(password), phone, role)
                db.session.add(user)
                db.session.commit()
                flash('New user created successfully')
                return redirect(url_for('login'))
        except:
            flash('Error creating new user')
            return redirect(url_for('register'))
        flash('Invalid credentials')
        return render_template('register.html')
    return render_template('register.html')

class admin:
    @app.route('/admin_dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role == '0':
            date_time = datetime.now()
            date = date_time.strftime("%Y-%m-%d")
            invoices_data = {}
            unique_invoices = invoices.query.with_entities(invoices.invoice_id).distinct().all()
            for invoice in unique_invoices:
                invoices_data[invoice.invoice_id] = {}
                invoices_data[invoice.invoice_id]['total'] = sum([int(i.total) for i in invoices.query.filter_by(invoice_id=invoice.invoice_id).all()])
                invoices_data[invoice.invoice_id]['date'] = invoices.query.filter_by(invoice_id=invoice.invoice_id).first().date.strftime("%Y-%m-%d %H:%M:%S")
            tables_occupied = db.session.query(tables, user_details).filter(tables.status == '1').join(user_details, tables.user == user_details.id).add_columns(tables.name, tables.table_id, tables.status, user_details.name, user_details.surname, tables.order_id).all()
            tables_unoccupied = tables.query.filter_by(status=0).all()
            data = {
                'tables_occupied': [tables_occupied, len(tables_occupied)],
                'tables_unoccupied': [tables_unoccupied, len(tables_unoccupied)],
                'date': str(date).split()[0],
                'invoices': invoices_data
            }
            return render_template('admin_dashboard.html', data=data)
        flash('You are not authorized to view this page')
        return redirect(url_for('logout'))


    @app.route('/add_table', methods=['POST'])
    @login_required
    def add_table():
        if current_user.role == '0':
            args = request.form
            name = args.get('name')
            status = 0
            user = None
            order_id = None
            try:
                table = tables(name, status, user, order_id)
                db.session.add(table)
                db.session.commit()
                flash('Table added successfully')
            except:
                flash('Table already exists')
            return redirect(url_for('dashboard'))
        flash('You are not authorized to view this page')
        return redirect(url_for('logout'))


    @app.route('/delete_table/<table_id>', methods=['GET'])
    @login_required
    def delete_table(table_id):
        if current_user.role == '0':
            table = tables.query.filter_by(table_id=table_id).first()
            db.session.delete(table)
            db.session.commit()
            flash('Table deleted successfully')
            return redirect(url_for('admin_dashboard'))
        flash('You are not authorized to delete an item')
        return redirect(url_for('logout'))


class owner:
    @app.route('/activate_table/<table_id>', methods=['GET'])
    @login_required
    def activate_table(table_id):
        if current_user.role in ['1','2']:
            table = tables.query.filter_by(table_id=table_id).first()
            table.status = 1
            table.order_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            table.user = current_user.id
            db.session.commit()
            flash('{} activated successfully'.format(table.name))
            return redirect(url_for('dashboard'))
        flash('You are not authorized to view this page')
        return redirect(url_for('dashboard'))


    @app.route('/owner_dashboard')
    @login_required
    def owner_dashboard():
        if current_user.role == '1':
            tables_occupied = tables.query.filter_by(status=1).all()
            tables_unoccupied = tables.query.filter_by(status=0).all()
            data = {
                'tables_occupied': [tables_occupied, len(tables_occupied)],
                'tables_unoccupied': [tables_unoccupied, len(tables_unoccupied)]
            }
            return render_template('owner_dashboard.html', data=data)
        flash('You are not authorized to view this page')
        return redirect(url_for('logout'))

    @app.route('/order/<order_id>', methods=['GET','POST'])
    @login_required
    def order(order_id):
        if current_user.role in ['1','2']:
            if request.method == 'GET':
                table = tables.query.filter_by(order_id=order_id).first()
                order = orders.query.filter_by(order_id=order_id).join(items, orders.item == items.item_id).add_columns(orders.id, items.name, items.rate, orders.quantity, orders.total).all()
                items_list = items.query.all()
                total_amount = orders.query.filter_by(order_id=order_id).with_entities(func.sum(orders.total)).scalar()
                unserved_orders = chef_orders.query.filter_by(order_id=order_id, sent=False).join(items, chef_orders.item == items.item_id).add_columns(items.name, chef_orders.quantity).all()
                data = {
                    'order_id': order_id,
                    'table': table,
                    'order': [order, len(order)],
                    'items_list': items_list,
                    'total_amount': 0 if total_amount == None else total_amount,
                    'unserved_orders': [unserved_orders, len(unserved_orders)]
                }
                return render_template('order.html', data=data)
        flash('You are not authorized to view this page')
        return redirect(url_for('dashboard'))


    @app.route('/order/<order_id>/add_item', methods=['POST'])
    @login_required
    def add_item(order_id):
        if current_user.role in ['1','2']:
            if request.method == 'POST':
                args = request.form
                item = args.get('item_id')
                quantity = int(args.get('quantity'))
                rate = int(items.query.filter_by(item_id=item).first().rate)
                fetch = orders.query.filter_by(order_id=order_id, item=args.get('item_id')).first()
                table_no = tables.query.filter_by(order_id=order_id).first().table_id
                data_to_chef = chef_orders(order_id, item, quantity, table_no, current_user.id, False)
                if fetch:
                    fetch.quantity = int(fetch.quantity) + int(quantity)
                    fetch.total = int(fetch.quantity) * rate
                else:
                    order_id = order_id
                    total = rate * quantity
                    user = current_user.id
                    order = orders(order_id, item, quantity, total, table_no, user)
                    db.session.add(order)
                db.session.add(data_to_chef)
                db.session.commit()
                flash('Item added successfully')
                return redirect(url_for('order', order_id=order_id))
        flash('You are not authorized to view this page')
        return redirect(url_for('dashboard'))


    @app.route('/order/<order_id>/print', methods=['GET'])
    @login_required
    def print_bill(order_id):
        if True:
            chef_data = chef_orders.query.filter_by(order_id=order_id).with_entities(chef_orders.item, func.sum(
                chef_orders.quantity)).group_by(chef_orders.item).order_by(chef_orders.item).filter(
                chef_orders.sent == True).all()
            order_data = orders.query.filter_by(order_id=order_id).with_entities(orders.item,
                                                                                 func.sum(orders.quantity)).group_by(
                orders.item).order_by(orders.item).all()
            if chef_data == order_data:
                table = tables.query.filter_by(order_id=order_id).first()
                order = orders.query.filter_by(order_id=order_id).join(items, orders.item == items.item_id).add_columns(
                    orders.id, items.name, items.rate, orders.quantity, orders.total).join(user_details, orders.user == user_details.id).add_columns(user_details.name, user_details.surname).all()
                total_amount = orders.query.filter_by(order_id=order_id).with_entities(func.sum(orders.total)).scalar()
                data = {
                    'order_id': order_id,
                    'table': table,
                    'order': [order, len(order)],
                    'total_amount': 0 if total_amount == None else total_amount,
                    'cgst': 0 if total_amount == None else total_amount * 0.025,
                    'sgst': 0 if total_amount == None else total_amount * 0.025,
                    'round_off': 0 if total_amount == None else total_amount + total_amount * 0.05 - round(total_amount + total_amount * 0.05),
                    'net_total': 0 if total_amount == None else round(total_amount + total_amount * 0.05),
                    'dt': datetime.now().strftime("%d %b %Y"),
                    'time': datetime.now().strftime("%I:%M:%S")
                }
                return render_template('print.html', data=data)
            else:
                flash(str([chef_data, order_data]))
                return redirect(url_for('order', order_id=order_id))
        flash('You are not authorized to view this page')
        return redirect(url_for('dashboard'))


    @app.route('/order/<order_id>/delete_item/<order_item_id>', methods=['GET'])
    @login_required
    def delete_item(order_id, order_item_id):
        if current_user.role in ['1','2']:
            order = orders.query.filter_by(id=order_item_id).first()
            db.session.delete(order)
            chef_order = chef_orders.query.filter_by(order_id=order_id, item=order.item).all()
            for i in chef_order:
                db.session.delete(i)
            db.session.commit()
            flash('Item deleted successfully')
            return redirect(url_for('order', order_id=order_id))
        flash('You are not authorized to view this page')
        return redirect(url_for('dashboard'))

    @app.route('/order/<order_id>/add_quantity/<order_item_id>', methods=['GET'])
    @login_required
    def add_quantity(order_id, order_item_id):
        if current_user.role in ['1','2']:
            order = orders.query.filter_by(id=order_item_id).first()
            order.quantity = int(order.quantity) + 1
            order.total = int(order.total) + int(items.query.filter_by(item_id=order.item).first().rate)
            chef = chef_orders(order_id, order.item, 1, order.table_no, current_user.id, False)
            db.session.add(chef)
            db.session.commit()
            flash('Quantity added successfully')
            return redirect(url_for('order', order_id=order_id))
        flash('You are not authorized to view this page')
        return redirect(url_for('dashboard'))

    @app.route('/order/<order_id>/subtract_quantity/<order_item_id>', methods=['GET'])
    @login_required
    def subtract_quantity(order_id, order_item_id):
        if current_user.role in ['1','2']:
            if request.method == 'GET':
                order = orders.query.filter_by(id=order_item_id).first()
                if int(order.quantity) > 1:
                    order.quantity = int(order.quantity) - 1
                    order.total = int(order.total) - int(items.query.filter_by(item_id=order.item).first().rate)
                    chef = chef_orders.query.filter_by(order_id=order_id, item=order.item).all()
                    if int(chef[-1].quantity) > 1:
                        chef[-1].quantity = int(chef[-1].quantity) - 1
                    else:
                        db.session.delete(chef[-1])
                    db.session.commit()
                    flash('Quantity subtracted successfully')
                    return redirect(url_for('order', order_id=order_id))
                else:
                    flash('Quantity cannot be less than 1')
                    return redirect(url_for('order', order_id=order_id))
            flash('Quantity added successfully')
            return redirect(url_for('order', order_id=order_id))
        flash('You are not authorized to view this page')
        return redirect(url_for('dashboard'))


    @app.route('/order/<order_id>/delete_order', methods=['GET'])
    @login_required
    def delete_order(order_id):
        if current_user.role in ['1','2']:
            order = orders.query.filter_by(order_id=order_id).all()
            for i in order:
                db.session.delete(i)
            table = tables.query.filter_by(order_id=order_id).first()
            table.status = 0
            table.order_id = None
            table.user = None
            chef = chef_orders.query.filter_by(order_id=order_id).all()
            for i in chef:
                db.session.delete(i)
            db.session.commit()
            flash('Order deleted successfully')
            return redirect(url_for('dashboard'))
        flash('You are not authorized to perform this action')
        return redirect(url_for('order', order_id=order_id))


    @app.route('/order/<order_id>/confirm', methods=['GET'])
    @login_required
    def confirm_order(order_id):
        if current_user.role == '1':
            chef_data = chef_orders.query.filter_by(order_id=order_id).with_entities(chef_orders.item, func.sum(chef_orders.quantity)).group_by(chef_orders.item).order_by(chef_orders.item).filter(chef_orders.sent == True).all()
            order_data = orders.query.filter_by(order_id=order_id).with_entities(orders.item, func.sum(orders.quantity)).group_by(orders.item).order_by(orders.item).all()
            if chef_data == order_data:
                order = orders.query.filter_by(order_id=order_id).all()
                invoice_id = order[0].order_id
                for i in order:
                    invoice = invoices(
                        invoice_id=invoice_id,
                        item = i.item,
                        quantity = i.quantity,
                        total = i.total,
                        date = i.date,
                        table_no = i.table_no,
                        user = i.user
                    )
                    db.session.add(invoice)
                table = tables.query.filter_by(order_id=order_id).first()
                table.status = 0
                table.order_id = None
                table.user = None
                for i in order:
                    db.session.delete(i)
                chef = chef_orders.query.filter_by(order_id=order_id).all()
                for i in chef:
                    db.session.delete(i)
                db.session.commit()
                flash('Order confirmed successfully')
                return redirect(url_for('dashboard'))
            else:
                flash('Order not confirmed. Please check the order and try again')
                return redirect(url_for('order', order_id=order_id))
            return render_template('test.html', data=[chef_data, order_data])
        flash('You are not authorized to view this page')
        return redirect(url_for('logout'))

    @app.route('/archive_item', methods=['GET'])
    @login_required
    def archives():
        if current_user.role in ['0','1']:
            invoice_ids = invoices.query.with_entities(invoices.invoice_id).distinct().order_by(invoices.invoice_id.desc()).all()
            invoice_data = {}
            for i in invoice_ids:
                invoice = invoices.query.filter_by(invoice_id=i[0]).all()
                date = str(invoice[0].date).split()
                total_amount = invoices.query.filter_by(invoice_id=i[0]).with_entities(func.sum(invoices.total)).first()[0]
                host = user_details.query.filter_by(id=invoice[0].user).first()
                invoice_data[i[0]] = [date, total_amount, host.name + ' ' + host.surname, invoice[0].table_no]
                for j in invoice:
                    invoice_data[i[0]].append({
                        'item': items.query.filter_by(item_id=j.item).first().name,
                        'quantity': j.quantity,
                        'table_no': j.table_no,
                    })
            return render_template('archives.html', data=invoice_data)
        flash('You are not authorized to view this page')
        return redirect(url_for('dashboard'))

    @app.route('/items', methods=['GET'])
    @login_required
    def owner_items():
        items_list = items.query.all()
        data = {
            'items_list': items_list
        }
        return render_template('items.html', data=data)

    @app.route('/items/update/<item_id>', methods=['GET', 'POST'])
    @login_required
    def update_items(item_id):
        if current_user.role == '0':
            if request.method == 'POST':
                name = request.form.get('item')
                rate = request.form.get('rate')
                item = items.query.filter_by(item_id=item_id).first()
                item.name = name
                item.rate = rate
                db.session.commit()
                flash('Item updated successfully')
                flash('Item updated successfully')
                return redirect(url_for('owner_items'))
            flash('Item updated successfully')
            return redirect(url_for('owner_items'))
        flash('You are not authorized to view this page')
        return redirect(url_for('owner_items'))


    @app.route('/items/delete/<item_id>', methods=['GET'])
    @login_required
    def delete_items(item_id):
        if current_user.role == '0':
            item = items.query.filter_by(item_id=item_id).first()
            db.session.delete(item)
            db.session.commit()
            flash('Item deleted successfully')
            return redirect(url_for('owner_items'))
        flash('You are not authorized to view this page')
        return redirect(url_for('owner_items'))


    @app.route('/items/add', methods=['GET', 'POST'])
    @login_required
    def add_items():
        if current_user.role == '0':
            if request.method == 'POST':
                name = request.form.get('item')
                rate = request.form.get('rate')
                item = items(
                    name=name,
                    rate=rate,
                    category=None,
                    sales=0
                )
                db.session.add(item)
                db.session.commit()
                flash('Item added successfully')
                return redirect(url_for('owner_items'))
            flash('Item added successfully')
            return redirect(url_for('owner_items'))
        flash('You are not authorized to view this page')
        return redirect(url_for('owner_items'))


@app.route('/summary', methods=['GET'])
@login_required
def summary():
    flash('Still under construction')
    return redirect(url_for('dashboard'))

class waiter:

        @app.route('/waiter', methods=['GET'])
        @login_required
        def waiter_dashboard():
            if current_user.role == '2':
                tables_occupied = tables.query.filter_by(status=1).all()
                tables_unoccupied = tables.query.filter_by(status=0).all()
                data = {
                    'tables_occupied': [tables_occupied, len(tables_occupied)],
                    'tables_unoccupied': [tables_unoccupied, len(tables_unoccupied)]
                }
                return render_template('owner_dashboard.html', data=data)
            flash('You are not authorized to view this page')
            return redirect(url_for('logout'))

class chef:

    @app.route('/chef_dashboard', methods=['GET'])
    @login_required
    def chef_dashboard():
        if current_user.role == '3':
            chef = chef_orders.query.join(items, chef_orders.item == items.item_id).add_columns(items.name, chef_orders.quantity, chef_orders.order_id, chef_orders.table_no).join(user_details, chef_orders.user == user_details.id).add_columns(user_details.name, user_details.surname).order_by(chef_orders.date.desc()).all()
            data = {
                'chef': chef,
                'str': lambda x: str(x)
            }
            return render_template('chef_dashboard.html', data=data)
        flash('You are not authorized to view this page')
        return redirect(url_for('logout'))

    @app.route('/chef_dashboard/confirm/<request_id>', methods=['GET'])
    @login_required
    def chef_confirm(request_id):
        if current_user.role == '3':
            order = chef_orders.query.filter_by(request_id=request_id).first()
            order.sent = True
            db.session.commit()
            flash('Order confirmed')
            return redirect(url_for('chef_dashboard'))
        flash('You are not authorized to view this page')
        return redirect(url_for('logout'))



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out')
    return redirect(url_for('login'))


db.create_all()
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=80)
