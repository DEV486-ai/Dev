from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "orders.db")

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/order", methods=["POST"])
def order():
    data = request.get_json(silent=True) or request.form

    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    address = (data.get("address") or "").strip()
    product = (data.get("product") or "").strip()
    quantity = str(data.get("quantity") or "1").strip()

    if not (name and phone and address and product):
        return jsonify({"message": "দয়া করে সব ঘর পূরণ করুন।"}), 400

    try:
        quantity = max(1, int(quantity))
    except ValueError:
        quantity = 1

    conn = get_db()
    conn.execute(
        "INSERT INTO orders (name, phone, address, product, quantity, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, phone, address, product, quantity, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": f"ধন্যবাদ {name}! আপনার অর্ডারটি গ্রহণ করা হয়েছে। শীঘ্রই আমরা যোগাযোগ করব।"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
