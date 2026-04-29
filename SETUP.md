# 🚀 MoneyMap – Firebase Edition Setup Guide

## ✅ What's Changed from the Original

| Area | Before (MySQL) | After (Firebase) |
|------|---------------|-----------------|
| Database | MySQL + `mysql-connector-python` | Cloud Firestore (NoSQL) |
| DB Helper | `database.py` with raw SQL | `firebase_db.py` with Firestore SDK |
| Models | `models.py` with `CREATE TABLE` | No schema needed – Firestore is schemaless |
| Auth | bcrypt + SQL Users table | bcrypt + Firestore `users` collection |
| Reports | ❌ Not available | ✅ PDF (ReportLab) + Excel (openpyxl) |
| UI | Basic custom CSS | Redesigned with Nunito font, animations, toasts |

---

## 📦 Project Structure

```
MoneyMap/
├── app.py                   ← Flask entry point
├── config.py                ← Firebase credentials path + collection names
├── firebase_db.py           ← Firestore CRUD helpers (replaces database.py)
├── auth.py                  ← Register / Login / Logout
├── routes.py                ← All API endpoints (30+)
├── reports.py               ← PDF + Excel report generation
├── requirements.txt         ← Python dependencies
│
├── firebase_config/
│   └── serviceAccountKey.json   ← ⚠️ Add yours here (NEVER commit to git)
│
├── static/
│   ├── css/style.css        ← Redesigned UI
│   └── js/main.js           ← Global JS utility module
│
└── templates/
    ├── base.html            ← Shared sidebar layout
    ├── login.html
    ├── register.html
    ├── dashboard.html       ← With PDF/Excel download buttons
    ├── analysis.html
    ├── categories.html
    ├── budgets.html
    ├── accounts.html
    ├── bills.html
    ├── subscriptions.html
    ├── trips.html
    ├── emi_tracker.html
    ├── investments.html
    └── settings.html
```

---

## 🔧 Step-by-Step Setup

### Step 1 – Create Firebase Project

1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Click **Add Project** → name it `moneymap` → Continue
3. Disable Google Analytics (optional) → Create Project
4. In the left sidebar: **Build → Firestore Database**
5. Click **Create database** → Start in **Production mode** → Choose a region → Done

### Step 2 – Download Service Account Key

1. Go to **Project Settings** (gear icon) → **Service accounts** tab
2. Click **Generate new private key** → Confirm
3. Save the JSON file as:  
   ```
   firebase_config/serviceAccountKey.json
   ```
   ⚠️ This file is already in `.gitignore`. Never commit it.

### Step 3 – Set Firestore Security Rules

In Firebase Console → Firestore Database → **Rules** tab, paste:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Backend only — Admin SDK bypasses these rules
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

Click **Publish**.

### Step 4 – Configure the App

Edit `config.py`:

```python
SECRET_KEY = "your-strong-random-secret-key-here"
FIREBASE_CREDENTIALS_PATH = "firebase_config/serviceAccountKey.json"
```

### Step 5 – Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 6 – Run the App

```bash
python app.py
```

Open your browser → [http://localhost:5000](http://localhost:5000)

---

## 📊 Using the Report Download Feature

Reports are available from:
- **Dashboard** → top-right buttons (PDF / Excel)  
- **Analysis** page → top-right buttons
- **Settings** page → Download Reports section
- **Investments** page → Excel button

### Selecting a month for reports:
Use the month picker on the Dashboard, then click the PDF/Excel button.  
The URL format is: `/reports/pdf?month=2024-11`

### What's included in each report:

**PDF Report:**
- Monthly summary (income / expense / balance) in coloured boxes
- Full transaction table with categories
- Budget vs. Actual comparison
- Subscriptions with total monthly cost
- Investment portfolio with gain/loss

**Excel Report (5 sheets):**
1. **Summary** – overview cards with colour formatting
2. **Transactions** – all transactions with colour-coded amounts
3. **Budgets** – budget vs. actual with remaining balance
4. **Subscriptions** – list with monthly total row
5. **Investments** – portfolio with gain/loss in green/red

---

## 🔥 Firestore Data Structure

Each collection stores documents per user, filtered by `user_id`:

```
users/                        (one doc per user)
  └── {uid}
        name, email, password(hashed), created_at, last_login

categories/                   (per user)
  └── {docId}
        user_id, name, type(income|expense)

transactions/
  └── {docId}
        user_id, category_id, type, amount, note, date

budgets/
  └── {docId}
        user_id, category_id, month(YYYY-MM), amount

trips/
  └── {docId}
        user_id, destination, start_date, end_date, budget

trip_expenses/
  └── {docId}
        trip_id, note, amount, date

bills/
  └── {docId}
        user_id, name, amount, due_day, category

bill_payments/
  └── {docId}
        bill_id, user_id, paid_month, paid_date

subscriptions/
  └── {docId}
        user_id, name, amount, renewal_day

subscription_payments/
  └── {docId}
        subscription_id, user_id, paid_month, paid_date

loans/
  └── {docId}
        user_id, loan_name, principal, rate, tenure, emi, total_int

emi_payments/
  └── {docId}
        loan_id, amount, paid_date, note

investments/
  └── {docId}
        user_id, name, type, amount, current_val, invest_date, note

preferences/
  └── {docId}
        user_id, currency, theme
```

---

## 🌐 Production Deployment (Gunicorn + Linux VPS)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or with `nohup` to keep running after logout:
```bash
nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app &
```

For HTTPS, put Nginx in front as a reverse proxy.

---

## 🛡️ Security Checklist

- [x] Passwords hashed with `bcrypt` (never stored in plaintext)
- [x] Firebase Admin SDK credentials stored outside source code
- [x] `serviceAccountKey.json` in `.gitignore`
- [x] Firestore rules deny all direct client access
- [x] All routes protected with `@login_required` decorator
- [x] Session-based auth with Flask secret key
- [ ] For production: set `debug=False` in `app.py`
- [ ] For production: use a proper `SECRET_KEY` (random, 32+ chars)
- [ ] For production: enable HTTPS
