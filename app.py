import streamlit as st
import pandas as pd
import db
import sender
import time
import re
import sqlite3

st.set_page_config(page_title="Bulk Email Tool", layout="wide", initial_sidebar_state="collapsed")

# ================= HACKER DARK THEME CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Fira Code', monospace !important;
    background-color: #07090e !important;
    color: #00ff66 !important;
}

.stApp {
    background: radial-gradient(circle at 50% 0%, #0d1912 0%, #050807 100%) !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #00ff66 !important;
    text-shadow: 0 0 10px rgba(0, 255, 102, 0.45);
    letter-spacing: 1px;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #0b110e !important;
    color: #00ffaa !important;
    border: 1px solid #00ff66 !important;
    border-radius: 4px !important;
    font-family: 'Fira Code', monospace !important;
}

.stButton > button {
    background-color: #0d2015 !important;
    color: #00ff66 !important;
    border: 1px solid #00ff66 !important;
    border-radius: 4px !important;
    font-family: 'Fira Code', monospace !important;
    font-weight: 700 !important;
}

.stButton > button:hover {
    background-color: #00ff66 !important;
    color: #050807 !important;
    box-shadow: 0 0 20px rgba(0, 255, 102, 0.8) !important;
}

.stAlert {
    background-color: #0a1410 !important;
    border: 1px solid #00ff66 !important;
    color: #00ffaa !important;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN GATEWAY =================
APP_PASSWORD = "Prateek@2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.get("password_input") == APP_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.error("❌ Galat Password!")

if not st.session_state.authenticated:
    st.markdown("### 🔒 Tool Login")
    st.text_input("Enter Password", type="password", key="password_input", on_change=check_password)
    st.button("Login >>", on_click=check_password)
    st.stop()
# ================================================

# Ensure database and table exist
db.init_db()

st.markdown("# ⚡ Bulk Email Outreach Tool")
st.caption("Active Status: Online | Delay: 4 Seconds | Manual Follow-up Mode")

tab1, tab2 = st.tabs(["🚀 Send Bulk Emails (Day 1)", "📊 Follow-up Tracker (Day 2)"])

with tab1:
    st.markdown("### 1. Sender Details")
    c1, c2, c3 = st.columns(3)
    with c1:
        sender_name = st.text_input("Sender Name (Aapka Naam)", placeholder="e.g. Rahul Sharma")
    with c2:
        s_email = st.text_input("Apna Gmail ID", placeholder="yourname@gmail.com")
    with c3:
        s_pass = st.text_input("16-Digit App Password", type="password")

    st.markdown("### 2. Target Email List")
    email_list_input = st.text_area("Jinhe email bhejna hai (Ek line mein ek email):", height=150)
    subject = st.text_input("Email Subject", value="Quick Inquiry")
    
    c4, c5 = st.columns(2)
    with c4:
        body_day1 = st.text_area("Pehla Email Content", height=150)
    with c5:
        body_day2 = st.text_area("Follow-up Content", height=150)

    if st.button("🚀 Send First Email >>", type="primary"):
        if not s_email or not s_pass or not email_list_input.strip():
            st.error("❌ Details adhoori hain! Kripya Gmail, App Password aur Emails bharein.")
        else:
            raw_emails = email_list_input.split('\n')
            valid_emails = [m.strip() for m in raw_emails if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', m.strip())]

            if not valid_emails:
                st.error("❌ Koi valid email nahi mila.")
            else:
                st.info(f"✅ Total {len(valid_emails)} emails bheje ja rahe hain...")
                progress_bar = st.progress(0)
                from_header = f"{sender_name} <{s_email}>" if sender_name.strip() else s_email

                for i, recipient in enumerate(valid_emails):
                    try:
                        sender.send_day1_email(s_email, s_pass, recipient, subject, body_day1, delay_hours=24, sender_header=from_header)
                    except TypeError:
                        sender.send_day1_email(s_email, s_pass, recipient, subject, body_day1, delay_hours=24)
                    except Exception as err:
                        st.error(f"❌ Error: {recipient} -> {err}")
                    
                    progress_bar.progress((i + 1) / len(valid_emails))
                    if i < len(valid_emails) - 1:
                        time.sleep(4)
                
                st.success("🎉 Sabhi pehle emails successfully chale gaye!")

with tab2:
    st.markdown("### 📊 Email History aur Follow-up Status")
    
    # Auto-repair DB check
    conn = sqlite3.connect("emails.db")
    cur = conn.cursor()
    cur.execute('''
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

    try:
        records = db.get_all_records()
    except Exception:
        records = []

    if records:
        df_records = pd.DataFrame(records, columns=["ID", "Receiver Email", "Subject", "Sent Time", "Follow-up Due Time", "Status"])
        st.dataframe(df_records, use_container_width=True)
    else:
        st.info("Abhi tak koi email record nahi hai.")

    st.markdown("---")
    st.write("Aap kisi bhi waqt pending emails ko follow-up bhej sakte hain:")
    
    if st.button("⚡ Bhejo Pending Follow-ups (Jab Chaho Tab) >>", type="primary"):
        if not s_email or not s_pass:
            st.error("❌ Pehle Tab 1 mein apna Gmail aur 16-Digit App Password dalein!")
        else:
            conn = sqlite3.connect("emails.db")
            cursor = conn.cursor()
            
            # Ensure table exists before executing SELECT
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

            cursor.execute("SELECT id, recipient, subject, message_id FROM campaigns WHERE status = 'PENDING'")
            pending = cursor.fetchall()
            conn.close()

            if not pending:
                st.warning("⚠️ Koi pending email nahi bacha hai!")
            else:
                st.info(f"🚀 {len(pending)} emails ko follow-up bheja ja raha hai...")
                p_bar = st.progress(0)
                from_header = f"{sender_name} <{s_email}>" if sender_name.strip() else s_email
                
                for idx, row in enumerate(pending):
                    cid, recipient, subj, initial_msg_id = row
                    try:
                        sender.send_smtp_message(s_email, s_pass, recipient, subj, body_day2, reply_to_id=initial_msg_id, sender_header=from_header)
                        db.mark_followup_complete(cid)
                        st.success(f"✅ Sent: {recipient}")
                    except TypeError:
                        sender.send_smtp_message(s_email, s_pass, recipient, subj, body_day2, reply_to_id=initial_msg_id)
                        db.mark_followup_complete(cid)
                        st.success(f"✅ Sent: {recipient}")
                    except Exception as e:
                        st.error(f"❌ Error: {recipient} -> {e}")
                    
                    p_bar.progress((idx + 1) / len(pending))
                    if idx < len(pending) - 1:
                        time.sleep(4)
                
                st.success("🎉 Sabhi follow-ups successfully chale gaye!")
