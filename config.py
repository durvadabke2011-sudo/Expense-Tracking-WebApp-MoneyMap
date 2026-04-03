"""
MoneyMap – Configuration
Replace the values below with your own Firebase project credentials.
"""

# ── Flask ──────────────────────────────────────────────────────────
SECRET_KEY = "moneymap_firebase_secret_2024"

# ── Firebase Service Account ───────────────────────────────────────
# Download your serviceAccountKey.json from:
#   Firebase Console → Project Settings → Service Accounts → Generate New Private Key
FIREBASE_CREDENTIALS_PATH = "firebase_config/serviceAccountKey.json"

# ── Firebase Project Config (for client-side SDK) ──────────────────
# Get these from: Firebase Console → Project Settings → General → Your Apps
FIREBASE_CONFIG = {
    "apiKey":            "YOUR_API_KEY",
    "authDomain":        "YOUR_PROJECT_ID.firebaseapp.com",
    "projectId":         "YOUR_PROJECT_ID",
    "storageBucket":     "YOUR_PROJECT_ID.appspot.com",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
    "appId":             "YOUR_APP_ID"
}

# ── Firestore Collection Names ─────────────────────────────────────
COLL_USERS          = "users"
COLL_CATEGORIES     = "categories"
COLL_TRANSACTIONS   = "transactions"
COLL_BUDGETS        = "budgets"
COLL_TRIPS          = "trips"
COLL_TRIP_EXPENSES  = "trip_expenses"
COLL_ACCOUNTS       = "accounts"
COLL_BILLS          = "bills"
COLL_BILL_PAYMENTS  = "bill_payments"
COLL_LOANS          = "loans"
COLL_EMI_PAYMENTS   = "emi_payments"
COLL_SUBSCRIPTIONS  = "subscriptions"
COLL_SUB_PAYMENTS   = "subscription_payments"
COLL_INVESTMENTS    = "investments"
COLL_SAVINGS        = "savings_goals"
COLL_BANK_TXN       = "bank_transactions"
COLL_PREFERENCES    = "preferences"
