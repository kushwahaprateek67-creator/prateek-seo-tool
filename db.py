import sqlite3
from datetime import datetime, timedelta, timezone

DB_NAME = "data_v3.db"  # Naya table version clean schema ke liye

def get_ist_now():
    ist_offset = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist_offset)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            subject TEXT,
            body TEXT,
            sent_at TEXT,
            followup_due TEXT,
            status TEXT,
            message_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_initial_email(recipient, subject, body, message_id="", due_time_or_hours=24):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now_ist = get_ist_now()
    
    if isinstance(due_time_or_hours, (int, float)):
        due_val = (now_ist + timedelta(hours=due_time_or_hours)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        due_val = str(due_time_or_hours)
    
    cursor.execute('''
        INSERT INTO campaigns (recipient, subject, body, sent_at, followup_due, status, message_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        recipient,
        subject,
        body,
        now_ist.strftime("%Y-%m-%d %H:%M:%S"),
        due_val,
        'PENDING',
        str(message_id)
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
