import sqlite3
from datetime import datetime, timedelta, timezone

DB_NAME = "data_v5.db"

def get_ist_now():
    ist_offset = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist_offset)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_email TEXT,
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

# Yeh check karega ki kisi ko pehle mail gaya hai ya nahi (Resume feature ke liye)
def is_email_sent_day1(recipient):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM campaigns WHERE recipient = ?", (recipient,))
    record = cursor.fetchone()
    conn.close()
    return record is not None

def log_initial_email(sender_email, recipient, subject, body, message_id="", due_time_or_hours=24):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now_ist = get_ist_now()
    due_val = (now_ist + timedelta(hours=due_time_or_hours)).strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO campaigns (sender_email, recipient, subject, body, sent_at, followup_due, status, message_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        sender_email, recipient, subject, body, 
        now_ist.strftime("%Y-%m-%d %H:%M:%S"), due_val, 'PENDING', str(message_id)
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
    cursor.execute("SELECT id, sender_email, recipient, subject, sent_at, followup_due, status FROM campaigns ORDER BY id DESC")
    records = cursor.fetchall()
    conn.close()
    return records
