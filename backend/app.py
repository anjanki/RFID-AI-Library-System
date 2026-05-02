import os
from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv

# 🔹 Load .env file
load_dotenv(dotenv_path=".env")

# 🔹 DEBUG (add here)
print("USER:", os.getenv("DB_USER"))
print("PASS:", os.getenv("DB_PASS"))

app = Flask(__name__)
# -----------------------------
# Database Connection
# -----------------------------
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

# -----------------------------
# Home Route
# -----------------------------
@app.route('/')
def home():
    return "RFID Smart Library Backend Running"

# -----------------------------
# RFID API
# -----------------------------
@app.route('/rfid')
def rfid():
    uid = request.args.get('uid')

    if not uid:
        return jsonify({"error": "UID missing"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Check book
    cursor.execute("SELECT * FROM books WHERE rfid=%s", (uid,))
    book = cursor.fetchone()

    if book:
        status = "allowed"
        book_name = book["book_name"]
    else:
        status = "denied"
        book_name = "Unknown"

    # Insert log
    cursor.execute(
        "INSERT INTO logs (rfid, result) VALUES (%s, %s)",
        (uid, status)
    )
    db.commit()

    cursor.close()
    db.close()

    return jsonify({
        "status": status,
        "book_name": book_name
    })

# -----------------------------
# Logs API
# -----------------------------
@app.route('/logs')
def get_logs():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT logs.id, logs.rfid, logs.timestamp, logs.result, books.book_name
        FROM logs
        LEFT JOIN books ON logs.rfid = books.rfid
        ORDER BY logs.id DESC
        LIMIT 100
    """)

    data = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(data)

# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)