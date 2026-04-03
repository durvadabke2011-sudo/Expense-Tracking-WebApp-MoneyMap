"""
MoneyMap – Authentication Blueprint (Firebase Edition)
Handles register / login / logout using Firestore user documents + bcrypt.
"""
from flask import Blueprint, request, session, redirect, url_for, render_template, flash
import bcrypt
from datetime import datetime
from firebase_db import create_doc, query_docs, update_doc, new_id, ts_now
from config import (COLL_USERS, COLL_CATEGORIES, COLL_PREFERENCES)

auth_bp = Blueprint('auth', __name__)

# ── DEFAULT CATEGORIES ────────────────────────────────────────────────
INCOME_CATS  = ['Salary', 'Freelance', 'Bonus', 'Investment Returns', 'Gifts', 'Other Income']
EXPENSE_CATS = [
    'Food & Dining', 'Transportation', 'Shopping', 'Utilities',
    'Healthcare', 'Entertainment', 'Education', 'Insurance',
    'Home & Rent', 'Personal Care', 'Phone & Internet',
    'Gifts & Donations', 'Other Expense'
]

def create_default_categories(user_id: str) -> None:
    for cat in INCOME_CATS:
        create_doc(COLL_CATEGORIES, {"user_id": user_id, "name": cat, "type": "income"})
    for cat in EXPENSE_CATS:
        create_doc(COLL_CATEGORIES, {"user_id": user_id, "name": cat, "type": "expense"})
    print(f"✅ Default categories created for user {user_id}")

# ── REGISTER ─────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        # Check duplicate email
        existing = query_docs(COLL_USERS, filters=[("email", "==", email)])
        if existing:
            flash('Email already registered. Please login.', 'error')
            return render_template('register.html')

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        uid    = new_id()

        create_doc(COLL_USERS, {
            "name":          name,
            "email":         email,
            "password":      hashed,
            "created_at":    ts_now(),
            "last_login":    None,
            "last_activity": None,
        }, doc_id=uid)

        # Default preferences
        create_doc(COLL_PREFERENCES, {"user_id": uid, "currency": "INR", "theme": "light"})
        # Default categories
        create_default_categories(uid)

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# ── LOGIN ─────────────────────────────────────────────────────────────
@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('routes.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        rows = query_docs(COLL_USERS, filters=[("email", "==", email)])
        if not rows:
            flash('Email not found. Please register.', 'error')
            return render_template('login.html')

        user = rows[0]
        if not bcrypt.checkpw(password.encode(), user['password'].encode()):
            flash('Incorrect password.', 'error')
            return render_template('login.html')

        now = ts_now()
        update_doc(COLL_USERS, user['id'], {"last_login": now, "last_activity": now})

        session['user_id']   = user['id']
        session['user_name'] = user['name']
        return redirect(url_for('routes.dashboard'))

    return render_template('login.html')

# ── LOGOUT ────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
