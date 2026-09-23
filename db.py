import sqlite3
from datetime import datetime

DB_PATH = "tracker.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            initial_msg_id TEXT,
            sent_at TIMESTAMP,
            follow_up_due TIMESTAMP,
            status TEXT DEFAULT 'PENDING_FOLLOWUP'
        )
    """)
    conn.commit()
    conn.close()

def log_initial_email(recipient, subject, msg_id, follow_up_due_dt):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO email_campaigns (recipient, subject, initial_msg_id, sent_at, follow_up_due, status)
        VALUES (?, ?, ?, ?, ?, 'PENDING_FOLLOWUP')
    """, (recipient, subject, msg_id, datetime.now(), follow_up_due_dt))
    conn.commit()
    conn.close()

def get_pending_followups():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        SELECT id, recipient, subject, initial_msg_id 
        FROM email_campaigns 
        WHERE status = 'PENDING_FOLLOWUP' AND follow_up_due <= ?
    """, (now,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_followup_complete(campaign_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE email_campaigns SET status = 'COMPLETED' WHERE id = ?", (campaign_id,))
    conn.commit()
    conn.close()

def get_all_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, recipient, subject, sent_at, follow_up_due, status FROM email_campaigns ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows