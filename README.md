# 💰 MoneyMap – Personal Finance Tracker

MoneyMap is a Flask-based expense tracking web application that helps users manage their daily expenses, categorize transactions, and analyze spending patterns through insightful reports and dashboards.

---

## 🚀 Features

- 📌 Add, edit, and delete expenses  
- 🗂️ Category-wise expense tracking  
- 📊 Interactive reports and summaries  
- 🔐 Secure data storage using Firebase  
- 📅 Track daily, monthly, and yearly spending  
- 📥 Download reports (PDF/Excel)  
- 🎯 Clean and user-friendly interface  

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, Bootstrap  
- **Backend:** Flask (Python)  
- **Database:** Firebase Firestore  
- **Libraries:** Pandas, NumPy  

---

## 📂 Project Structure


MoneyMap/
│── app.py
│── routes.py
│── auth.py
│── firebase_db.py
│── config.py
│── reports.py
│── requirements.txt
│── SETUP.md
│
├── templates/
├── static/
├── firebase_config/ (ignored in git)
└── .gitignore


---

## ⚙️ Setup Instructions

Follow the steps in `SETUP.md` to run the project locally.

### Quick Setup:


git clone https://github.com/durvadabke2011-sudo/Expense-Tracking-WebApp-MoneyMap.git

cd Expense-Tracking-WebApp-MoneyMap
pip install -r requirements.txt
python app.py


---

## 🔐 Environment Setup

- Add your Firebase credentials file in:

firebase_config/serviceAccountKey.json

- This file is ignored in `.gitignore` for security.

---

## 📸 Screenshots

_Add screenshots of your app here (dashboard, reports, etc.)_

---

## 🎯 Use Case

MoneyMap helps users:
- Track expenses efficiently  
- Understand spending habits  
- Improve budgeting and financial planning  

---
