"""
MoneyMap – Feature Routes Blueprint (Firebase Edition)
All page renders + JSON API endpoints.
"""
from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify
from functools import wraps
from datetime import datetime, date
import calendar
from firebase_db import (
    create_doc, get_doc, query_docs, update_doc, delete_doc,
    delete_docs, new_id, ts_now
)
from config import *

routes_bp = Blueprint('routes', __name__)

# ── Auth guard ────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def uid():
    return session['user_id']

# ── Helpers ───────────────────────────────────────────────────────────
def today_str():
    return date.today().isoformat()

def current_month():
    return date.today().strftime('%Y-%m')

# ═══════════════════════════════════════════════════════════════════════
# PAGE ROUTES
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@routes_bp.route('/analysis')
@login_required
def analysis():
    return render_template('analysis.html')

@routes_bp.route('/categories')
@login_required
def categories():
    return render_template('categories.html')

@routes_bp.route('/budgets')
@login_required
def budgets():
    return render_template('budgets.html')

@routes_bp.route('/trips')
@login_required
def trips():
    return render_template('trips.html')

@routes_bp.route('/accounts')
@login_required
def accounts():
    return render_template('accounts.html')

@routes_bp.route('/bills')
@login_required
def bills():
    return render_template('bills.html')

@routes_bp.route('/subscriptions')
@login_required
def subscriptions():
    return render_template('subscriptions.html')

@routes_bp.route('/emi-tracker')
@login_required
def emi_tracker():
    return render_template('emi_tracker.html')

@routes_bp.route('/investments')
@login_required
def investments():
    return render_template('investments.html')

@routes_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

# ═══════════════════════════════════════════════════════════════════════
# API – DASHBOARD SUMMARY
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/dashboard')
@login_required
def api_dashboard():
    month = request.args.get('month', current_month())
    txns  = query_docs(COLL_TRANSACTIONS, filters=[("user_id", "==", uid())])
    month_txns = [t for t in txns if t.get('date', '').startswith(month)]

    income  = sum(t['amount'] for t in month_txns if t['type'] == 'income')
    expense = sum(t['amount'] for t in month_txns if t['type'] == 'expense')
    balance = income - expense

    # Recent transactions (latest 10)
    all_sorted = sorted(txns, key=lambda x: x.get('date',''), reverse=True)[:10]

    # Category breakdown for month
    cats = query_docs(COLL_CATEGORIES, filters=[("user_id", "==", uid())])
    cat_map = {c['id']: c['name'] for c in cats}

    recent = []
    for t in all_sorted:
        recent.append({
            'id':       t['id'],
            'type':     t['type'],
            'amount':   t['amount'],
            'note':     t.get('note', ''),
            'date':     t.get('date', ''),
            'category': cat_map.get(t.get('category_id', ''), 'Uncategorised'),
        })

    # Financial health score
    score   = _health_score(income, expense, txns)
    suggestions = _suggestions(income, expense)

    return jsonify({
        'income':   income,
        'expense':  expense,
        'balance':  balance,
        'recent':   recent,
        'score':    score,
        'suggestions': suggestions,
        'month':    month,
    })

def _health_score(income, expense, all_txns):
    if income == 0:
        return 30
    ratio = expense / income
    score = 100
    if ratio > 0.9:  score -= 40
    elif ratio > 0.7: score -= 20
    elif ratio > 0.5: score -= 10
    return max(10, min(100, int(score)))

def _suggestions(income, expense):
    tips = []
    if income == 0:
        tips.append("💡 Start by logging your income to get personalised insights.")
        return tips
    ratio = expense / income
    if ratio > 0.9:
        tips.append("⚠️ You are spending over 90% of your income. Consider cutting discretionary expenses.")
    elif ratio > 0.7:
        tips.append("📉 Spending is above 70% of income. Try to save at least 20%.")
    else:
        tips.append("✅ Great! You are saving a healthy portion of your income.")
    if expense > income:
        tips.append("🚨 Expenses exceed income this month. Review your budget immediately.")
    return tips

# ═══════════════════════════════════════════════════════════════════════
# API – TRANSACTIONS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/transactions', methods=['GET'])
@login_required
def api_get_transactions():
    month = request.args.get('month', current_month())
    txns  = query_docs(COLL_TRANSACTIONS, filters=[("user_id", "==", uid())])
    cats  = query_docs(COLL_CATEGORIES,   filters=[("user_id", "==", uid())])
    cat_map = {c['id']: c['name'] for c in cats}

    result = []
    for t in txns:
        if not t.get('date', '').startswith(month):
            continue
        result.append({
            'id':       t['id'],
            'type':     t['type'],
            'amount':   t['amount'],
            'note':     t.get('note', ''),
            'date':     t['date'],
            'category': cat_map.get(t.get('category_id', ''), 'Uncategorised'),
            'category_id': t.get('category_id', ''),
        })
    result.sort(key=lambda x: x['date'], reverse=True)
    return jsonify(result)

@routes_bp.route('/api/transactions', methods=['POST'])
@login_required
def api_add_transaction():
    data = request.json
    doc_id = create_doc(COLL_TRANSACTIONS, {
        'user_id':     uid(),
        'category_id': data.get('category_id', ''),
        'type':        data['type'],
        'amount':      float(data['amount']),
        'note':        data.get('note', ''),
        'date':        data['date'],
    })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/transactions/<txn_id>', methods=['DELETE'])
@login_required
def api_delete_transaction(txn_id):
    delete_doc(COLL_TRANSACTIONS, txn_id)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════════════════════
# API – CATEGORIES
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/categories', methods=['GET'])
@login_required
def api_get_categories():
    cats = query_docs(COLL_CATEGORIES, filters=[("user_id", "==", uid())])
    return jsonify(cats)

@routes_bp.route('/api/categories', methods=['POST'])
@login_required
def api_add_category():
    data = request.json
    doc_id = create_doc(COLL_CATEGORIES, {
        'user_id': uid(),
        'name':    data['name'],
        'type':    data['type'],
    })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/categories/<cat_id>', methods=['DELETE'])
@login_required
def api_delete_category(cat_id):
    delete_doc(COLL_CATEGORIES, cat_id)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════════════════════
# API – BUDGETS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/budgets', methods=['GET'])
@login_required
def api_get_budgets():
    month   = request.args.get('month', current_month())
    budgets = query_docs(COLL_BUDGETS, filters=[
        ("user_id", "==", uid()),
        ("month",   "==", month)
    ])
    txns = query_docs(COLL_TRANSACTIONS, filters=[("user_id", "==", uid())])
    cats = query_docs(COLL_CATEGORIES,   filters=[("user_id", "==", uid())])
    cat_map = {c['id']: c['name'] for c in cats}

    result = []
    for b in budgets:
        spent = sum(
            t['amount'] for t in txns
            if t['type'] == 'expense'
            and t.get('category_id') == b.get('category_id')
            and t.get('date', '').startswith(month)
        )
        result.append({
            'id':       b['id'],
            'category': cat_map.get(b.get('category_id', ''), 'Unknown'),
            'category_id': b.get('category_id', ''),
            'amount':   b['amount'],
            'spent':    spent,
            'month':    b['month'],
        })
    return jsonify(result)

@routes_bp.route('/api/budgets', methods=['POST'])
@login_required
def api_add_budget():
    data = request.json
    doc_id = create_doc(COLL_BUDGETS, {
        'user_id':     uid(),
        'category_id': data.get('category_id', ''),
        'month':       data.get('month', current_month()),
        'amount':      float(data['amount']),
    })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/budgets/<bud_id>', methods=['DELETE'])
@login_required
def api_delete_budget(bud_id):
    delete_doc(COLL_BUDGETS, bud_id)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════════════════════
# API – ACCOUNTS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/accounts', methods=['GET'])
@login_required
def api_get_accounts():
    return jsonify(query_docs(COLL_ACCOUNTS, filters=[("user_id", "==", uid())]))

@routes_bp.route('/api/accounts', methods=['POST'])
@login_required
def api_add_account():
    data = request.json
    doc_id = create_doc(COLL_ACCOUNTS, {
        'user_id': uid(),
        'name':    data['name'],
        'type':    data['type'],
        'balance': float(data.get('balance', 0)),
    })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/accounts/<acc_id>', methods=['DELETE'])
@login_required
def api_delete_account(acc_id):
    delete_doc(COLL_ACCOUNTS, acc_id)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════════════════════
# API – BILLS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/bills', methods=['GET'])
@login_required
def api_get_bills():
    month = current_month()
    bills = query_docs(COLL_BILLS, filters=[("user_id", "==", uid())])
    paid  = query_docs(COLL_BILL_PAYMENTS, filters=[
        ("user_id",    "==", uid()),
        ("paid_month", "==", month),
    ])
    paid_ids = {p['bill_id'] for p in paid}

    today = date.today()
    result = []
    for b in bills:
        due_day  = b.get('due_day', 1)
        days_left = due_day - today.day
        result.append({
            'id':       b['id'],
            'name':     b['name'],
            'amount':   b['amount'],
            'due_day':  due_day,
            'category': b.get('category', ''),
            'paid':     b['id'] in paid_ids,
            'days_left': days_left,
        })
    return jsonify(result)

@routes_bp.route('/api/bills', methods=['POST'])
@login_required
def api_add_bill():
    data = request.json
    doc_id = create_doc(COLL_BILLS, {
        'user_id':  uid(),
        'name':     data['name'],
        'amount':   float(data['amount']),
        'due_day':  int(data['due_day']),
        'category': data.get('category', ''),
    })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/bills/<bill_id>/pay', methods=['POST'])
@login_required
def api_pay_bill(bill_id):
    data  = request.json
    month = current_month()
    create_doc(COLL_BILL_PAYMENTS, {
        'bill_id':    bill_id,
        'user_id':    uid(),
        'paid_month': month,
        'paid_date':  data.get('date', today_str()),
    })
    # Also record as expense transaction
    bill = get_doc(COLL_BILLS, bill_id)
    if bill:
        create_doc(COLL_TRANSACTIONS, {
            'user_id': uid(),
            'type':    'expense',
            'amount':  bill['amount'],
            'note':    f"Bill: {bill['name']}",
            'date':    data.get('date', today_str()),
        })
    return jsonify({'ok': True})

@routes_bp.route('/api/bills/<bill_id>', methods=['DELETE'])
@login_required
def api_delete_bill(bill_id):
    delete_doc(COLL_BILLS, bill_id)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════════════════════
# API – SUBSCRIPTIONS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/subscriptions', methods=['GET'])
@login_required
def api_get_subscriptions():
    month = current_month()
    subs  = query_docs(COLL_SUBSCRIPTIONS, filters=[("user_id", "==", uid())])
    paid  = query_docs(COLL_SUB_PAYMENTS, filters=[
        ("user_id",    "==", uid()),
        ("paid_month", "==", month),
    ])
    paid_ids = {p['subscription_id'] for p in paid}

    today   = date.today()
    yr, mo  = today.year, today.month
    _, last = calendar.monthrange(yr, mo)

    result = []
    for s in subs:
        day = s.get('renewal_day', 1)
        day = min(day, last)
        renewal = date(yr, mo, day)
        if renewal < today:
            mo2  = mo + 1 if mo < 12 else 1
            yr2  = yr if mo < 12 else yr + 1
            _, l2 = calendar.monthrange(yr2, mo2)
            renewal = date(yr2, mo2, min(s['renewal_day'], l2))
        days_left = (renewal - today).days
        result.append({
            'id':           s['id'],
            'name':         s['name'],
            'amount':       s['amount'],
            'renewal_day':  s.get('renewal_day', 1),
            'next_renewal': renewal.isoformat(),
            'days_left':    days_left,
            'paid':         s['id'] in paid_ids,
        })
    return jsonify(result)

@routes_bp.route('/api/subscriptions', methods=['POST'])
@login_required
def api_add_subscription():
    data = request.json
    doc_id = create_doc(COLL_SUBSCRIPTIONS, {
        'user_id':     uid(),
        'name':        data['name'],
        'amount':      float(data['amount']),
        'renewal_day': int(data['renewal_day']),
    })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/subscriptions/<sub_id>/pay', methods=['POST'])
@login_required
def api_pay_subscription(sub_id):
    data  = request.json
    month = current_month()
    create_doc(COLL_SUB_PAYMENTS, {
        'subscription_id': sub_id,
        'user_id':         uid(),
        'paid_month':      month,
        'paid_date':       data.get('date', today_str()),
    })
    sub = get_doc(COLL_SUBSCRIPTIONS, sub_id)
    if sub:
        create_doc(COLL_TRANSACTIONS, {
            'user_id': uid(),
            'type':    'expense',
            'amount':  sub['amount'],
            'note':    f"Subscription: {sub['name']}",
            'date':    data.get('date', today_str()),
        })
    return jsonify({'ok': True})

@routes_bp.route('/api/subscriptions/<sub_id>', methods=['DELETE'])
@login_required
def api_delete_subscription(sub_id):
    delete_doc(COLL_SUBSCRIPTIONS, sub_id)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════════════════════
# API – TRIPS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/trips', methods=['GET'])
@login_required
def api_get_trips():
    trips = query_docs(COLL_TRIPS, filters=[("user_id", "==", uid())])
    result = []
    for t in trips:
        expenses = query_docs(COLL_TRIP_EXPENSES, filters=[("trip_id", "==", t['id'])])
        spent = sum(e['amount'] for e in expenses)
        result.append({**t, 'spent': spent, 'expenses': expenses})
    return jsonify(result)

@routes_bp.route('/api/trips', methods=['POST'])
@login_required
def api_add_trip():
    data = request.json
    doc_id = create_doc(COLL_TRIPS, {
        'user_id':     uid(),
        'destination': data['destination'],
        'start_date':  data['start_date'],
        'end_date':    data['end_date'],
        'budget':      float(data.get('budget', 0)),
    })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/trips/<trip_id>/expenses', methods=['POST'])
@login_required
def api_add_trip_expense(trip_id):
    data = request.json
    doc_id = create_doc(COLL_TRIP_EXPENSES, {
        'trip_id': trip_id,
        'note':    data.get('note', ''),
        'amount':  float(data['amount']),
        'date':    data['date'],
    })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/trips/<trip_id>', methods=['DELETE'])
@login_required
def api_delete_trip(trip_id):
    delete_docs(COLL_TRIP_EXPENSES, [("trip_id", "==", trip_id)])
    delete_doc(COLL_TRIPS, trip_id)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════════════════════
# API – EMI / LOANS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/loans', methods=['GET'])
@login_required
def api_get_loans():
    loans = query_docs(COLL_LOANS, filters=[("user_id", "==", uid())])
    result = []
    for l in loans:
        payments = query_docs(COLL_EMI_PAYMENTS, filters=[("loan_id", "==", l['id'])])
        paid_total = sum(p['amount'] for p in payments)
        result.append({**l, 'paid_total': paid_total, 'payments': payments})
    return jsonify(result)

@routes_bp.route('/api/loans', methods=['POST'])
@login_required
def api_add_loan():
    data = request.json
    principal = float(data['principal'])
    rate      = float(data['rate'])
    tenure    = int(data['tenure'])
    r = rate / 1200
    if r > 0:
        emi = principal * r * (1 + r)**tenure / ((1 + r)**tenure - 1)
    else:
        emi = principal / tenure
    total_int = emi * tenure - principal
    doc_id = create_doc(COLL_LOANS, {
        'user_id':   uid(),
        'loan_name': data.get('loan_name', 'My Loan'),
        'principal': principal,
        'rate':      rate,
        'tenure':    tenure,
        'emi':       round(emi, 2),
        'total_int': round(total_int, 2),
    })
    return jsonify({'id': doc_id, 'emi': round(emi, 2), 'total_int': round(total_int, 2)}), 201

@routes_bp.route('/api/loans/<loan_id>/pay', methods=['POST'])
@login_required
def api_pay_emi(loan_id):
    data = request.json
    doc_id = create_doc(COLL_EMI_PAYMENTS, {
        'loan_id':   loan_id,
        'amount':    float(data['amount']),
        'paid_date': data.get('date', today_str()),
        'note':      data.get('note', ''),
    })
    loan = get_doc(COLL_LOANS, loan_id)
    if loan:
        create_doc(COLL_TRANSACTIONS, {
            'user_id': uid(),
            'type':    'expense',
            'amount':  float(data['amount']),
            'note':    f"EMI: {loan.get('loan_name','Loan')}",
            'date':    data.get('date', today_str()),
        })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/loans/<loan_id>', methods=['DELETE'])
@login_required
def api_delete_loan(loan_id):
    delete_docs(COLL_EMI_PAYMENTS, [("loan_id", "==", loan_id)])
    delete_doc(COLL_LOANS, loan_id)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════════════════════
# API – INVESTMENTS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/investments', methods=['GET'])
@login_required
def api_get_investments():
    return jsonify(query_docs(COLL_INVESTMENTS, filters=[("user_id", "==", uid())]))

@routes_bp.route('/api/investments', methods=['POST'])
@login_required
def api_add_investment():
    data = request.json
    doc_id = create_doc(COLL_INVESTMENTS, {
        'user_id':     uid(),
        'name':        data['name'],
        'type':        data['type'],
        'amount':      float(data['amount']),
        'current_val': float(data.get('current_val', data['amount'])),
        'invest_date': data['invest_date'],
        'note':        data.get('note', ''),
    })
    return jsonify({'id': doc_id}), 201

@routes_bp.route('/api/investments/<inv_id>', methods=['DELETE'])
@login_required
def api_delete_investment(inv_id):
    delete_doc(COLL_INVESTMENTS, inv_id)
    return jsonify({'ok': True})

# ═══════════════════════════════════════════════════════════════════════
# API – ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/analysis')
@login_required
def api_analysis():
    txns = query_docs(COLL_TRANSACTIONS, filters=[("user_id", "==", uid())])
    cats = query_docs(COLL_CATEGORIES,   filters=[("user_id", "==", uid())])
    cat_map = {c['id']: c['name'] for c in cats}

    # Monthly summary – last 6 months
    monthly = {}
    for t in txns:
        m = t.get('date', '')[:7]
        if m not in monthly:
            monthly[m] = {'income': 0, 'expense': 0}
        monthly[m][t['type']] = monthly[m].get(t['type'], 0) + t['amount']

    months_sorted = sorted(monthly.keys())[-6:]
    monthly_data  = {m: monthly[m] for m in months_sorted}

    # Category breakdown – current month
    cm = current_month()
    cat_breakdown = {}
    for t in txns:
        if t.get('date', '').startswith(cm) and t['type'] == 'expense':
            cat = cat_map.get(t.get('category_id', ''), 'Other')
            cat_breakdown[cat] = cat_breakdown.get(cat, 0) + t['amount']

    return jsonify({
        'monthly':       monthly_data,
        'cat_breakdown': cat_breakdown,
        'total_income':  sum(t['amount'] for t in txns if t['type'] == 'income'),
        'total_expense': sum(t['amount'] for t in txns if t['type'] == 'expense'),
    })

# ═══════════════════════════════════════════════════════════════════════
# API – SETTINGS
# ═══════════════════════════════════════════════════════════════════════

@routes_bp.route('/api/settings', methods=['GET'])
@login_required
def api_get_settings():
    prefs = query_docs(COLL_PREFERENCES, filters=[("user_id", "==", uid())])
    return jsonify(prefs[0] if prefs else {'currency': 'INR', 'theme': 'light'})

@routes_bp.route('/api/settings', methods=['POST'])
@login_required
def api_save_settings():
    data  = request.json
    prefs = query_docs(COLL_PREFERENCES, filters=[("user_id", "==", uid())])
    if prefs:
        update_doc(COLL_PREFERENCES, prefs[0]['id'], {
            'currency': data.get('currency', 'INR'),
            'theme':    data.get('theme', 'light'),
        })
    else:
        create_doc(COLL_PREFERENCES, {
            'user_id':  uid(),
            'currency': data.get('currency', 'INR'),
            'theme':    data.get('theme', 'light'),
        })
    return jsonify({'ok': True})
