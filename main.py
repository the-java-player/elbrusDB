
from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_NAME = "licenses.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def create_table():
    """Создаём таблицу при первом запросе"""
    try:
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS licenses (
                key TEXT PRIMARY KEY,
                is_used INTEGER DEFAULT 0,
                hardware_id TEXT,
                activated_at TEXT
            )
        """)
        conn.commit()
        conn.close()
    except:
        pass

@app.route('/activate', methods=['POST'])
def activate():
    data = request.get_json()
    license_key = data.get('license_key')
    hardware_id = data.get('hardware_id')
    
    if not license_key or not hardware_id:
        return jsonify({"error": "Нужны license_key и hardware_id"}), 400
    
    conn = get_db()
    cur = conn.execute("SELECT * FROM licenses WHERE key = ?", (license_key,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Неверный ключ"}), 400
    
    if row['is_used']:
        conn.close()
        return jsonify({"error": "Ключ уже активирован"}), 400
    
    # Активируем
    conn.execute(
        "UPDATE licenses SET is_used = 1, hardware_id = ?, activated_at = ? WHERE key = ?",
        (hardware_id, datetime.now().isoformat(), license_key)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"status": "ok", "message": "Активация успешна"}), 200

@app.route('/')
def index():
    return "License server is working!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
