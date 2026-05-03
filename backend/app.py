from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timezone, timedelta
from functools import wraps
import os

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'teen_vault.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-teen-vault-key' 

db = SQLAlchemy(app)
CORS(app)

# --- DATABASE MODELS ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='teen')  # 'teen' or 'parent'
    balance = db.Column(db.Float, default=0.0)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    expenses = db.relationship('Expense', backref='owner', lazy=True, cascade="all, delete-orphan")
    wishlist = db.relationship('WishlistItem', backref='owner', lazy=True, cascade="all, delete-orphan")

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Initialize Database
with app.app_context():
    db.create_all()

# --- UTILITY: TOKEN DECORATOR ---

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            # Expected format: "Bearer <token>"
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header

        if not token:
            return jsonify({'detail': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.session.get(User, data['sub'])
        except Exception as e:
            return jsonify({'detail': 'Token is invalid or expired'}), 401
            
        return f(current_user, *args, **kwargs)
    return decorated

# --- AUTH ROUTES ---

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"detail": "Username already exists"}), 400

    new_user = User(
        username=data.get('username'),
        password=generate_password_hash(data.get('password')),
        role=data.get('role', 'teen'),
        balance=0.0
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({"detail": "Invalid username or password"}), 401

    token = jwt.encode({
        'sub': user.id,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        "access_token": token,
        "role": user.role,
        "username": user.username
    }), 200

# --- DASHBOARD & FEATURE ROUTES ---

@app.route('/dashboard-data', methods=['GET'])
@token_required
def get_dashboard(current_user):
    # Base data every user gets
    response_data = {
        "username": current_user.username,
        "balance": current_user.balance,
        "role": current_user.role
    }
    
    if current_user.role == 'teen':
        # Teen sees their own wishlist and spending history
        response_data["wishlist"] = [
            {"id": i.id, "name": i.item_name, "price": i.price} for i in current_user.wishlist
        ]
        response_data["expenses"] = [
            {"amount": e.amount, "category": e.category, "date": e.date.strftime("%Y-%m-%d")} 
            for e in current_user.expenses
        ]
    else:
        # Parent sees a summary of all their linked children
        children = User.query.filter_by(parent_id=current_user.id).all()
        response_data["children"] = [
            {"username": c.username, "balance": c.balance} for c in children
        ]
        
    return jsonify(response_data), 200

@app.route('/add-expense', methods=['POST'])
@token_required
def add_expense(current_user):
    data = request.get_json()
    amount = float(data.get('amount', 0))
    
    if current_user.balance < amount:
        return jsonify({"detail": "Insufficient pocket money balance!"}), 400
    
    new_expense = Expense(
        amount=amount, 
        category=data.get('category', 'General'), 
        user_id=current_user.id
    )
    current_user.balance -= amount
    
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({"message": "Expense logged!", "new_balance": current_user.balance}), 200

@app.route('/add-wishlist', methods=['POST'])
@token_required
def add_wishlist(current_user):
    data = request.get_json()
    new_item = WishlistItem(
        item_name=data.get('name'),
        price=float(data.get('price', 0)),
        user_id=current_user.id
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Added to wishlist!"}), 201

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)