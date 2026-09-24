import sqlite3
from datetime import datetime, timedelta
import pytz

DB_NAME = "data_v2.db" # Naya naam, taaki purana error na aaye

def get_ist_now():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            subject TEXT,
            sent_at TEXT,
            followup_due TEXT,
            status TEXT,
            message_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_initial_email(recipient, subject, message_id="", delay_hours=24):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now_ist = get_ist_now()
    due_ist = now_ist + timedelta(hours=delay_hours)
    
    cursor.execute('''
        INSERT INTO campaigns (recipient, subject, sent_at, followup_due, status, message_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        recipient,
        subject,
        now_ist.strftime("%Y-%m-%d %H:%M:%S"),
        due_ist.strftime("%Y-%m-%d %H:%M:%S"),
        'PENDING',
        message_id
    ))
    conn.commit()
    conn.close()

def mark_followup_complete(record_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE campaigns SET status = 'COMPLETED' WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

def get_all_records():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, recipient, subject, sent_at, followup_due, status FROM campaigns ORDER BY id DESC")
    records = cursor.fetchall()
    conn.close()
    return records
