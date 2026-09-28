import streamlit as st
import pandas as pd
import math
import db
import sender
import time
import re
import sqlite3
import os

st.set_page_config(page_title="Bulk Auto Outreach", layout="wide", initial_sidebar_state="collapsed")

# ================= DARK THEME =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Fira Code', monospace !important; background-color: #07090e !important; color: #00ff66 !important; }
.stApp { background: radial-gradient(circle at 50% 0%, #0d1912 0%, #050807 100%) !important; }
</style>
""", unsafe_allow_html=True)

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

db.init_db()

st.markdown("# ⚡ Bulk Auto Engine (100 Accounts -> 2500 Emails)")
st.caption("Auto-Rotation | Resumable | Quoted Threads")

tab1, tab2 = st.tabs(["🚀 Auto Day 1 (Send Bulk)", "📊 Auto Day 2 (Follow-ups & Backup)"])

# ================= TAB 1 : DAY 1 SENDING =================
with tab1:
    st.markdown("### 1. Upload CSV Files")
    st.info("💡 Senders CSV me 3 column hone chahiye: 'Email', 'Password', 'Name'. Targets CSV me 1 column: 'Target_Email'.")
    
    col1, col2 = st.columns(2)
    with col1:
        senders_csv = st.file_uploader("📥 Upload Senders CSV (100 Accounts)", type=['csv'], key="s1")
    with col2:
        targets_csv = st.file_uploader("📥 Upload Targets CSV (2500 Leads)", type=['csv'], key="t1")

    subject = st.text_input("Email Subject", value="Quick Inquiry")
    body_day1 = st.text_area("Pehla Email Content", height=150)

    if st.button("🚀 Start Bulk Sending (Auto-Rotate) >>", type="primary"):
        if not senders_csv or not targets_csv:
            st.error("❌ Dono CSV files upload karna zaroori hai!")
        else:
            df_senders = pd.read_csv(senders_csv)
            df_targets = pd.read_csv(targets_csv)
            
            senders_list = df_senders.to_dict('records')
            targets_list = df_targets['Target_Email'].dropna().tolist()
            
            # Clean emails
            targets_list = [t.strip() for t in targets_list if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', t.strip())]
            
            if not senders_list or not targets_list:
                st.error("❌ CSV file khali hai ya galat format me hai.")
            else:
                total_senders = len(senders_list)
                total_targets = len(targets_list)
                chunk_size = math.ceil(total_targets / total_senders)
                
                st.success(f"✅ Loaded {total_senders} Senders aur {total_targets} Targets. Har account se lagbhag {chunk_size} email jayenge.")
                
                p_bar = st.progress(0)
                status_text = st.empty()
                
                sent_count = 0
                for index, s_data in enumerate(senders_list):
                    s_email = s_data['Email'].strip()
                    s_pass = str(s_data['Password']).strip()
                    s_name = str(s_data.get('Name', '')).strip()
                    from_header = f"{s_name} <{s_email}>" if s_name else s_email
                    
                    # Us sender ka hissa (Chunk)
                    start_idx = index * chunk_size
                    end_idx = start_idx + chunk_size
                    my_targets = targets_list[start_idx:end_idx]
                    
                    for target in my_targets:
                        # Resume Check: Agar email pehle ja chuka hai toh skip karo
                        if db.is_email_sent_day1(target):
                            sent_count += 1
                            continue
                            
                        status_text.text(f"⏳ Bhej rahe hain... Sender: {s_email} -> Target: {target}")
                        try:
                            sender.send_day1_email(s_email, s_pass, target, subject, body_day1, delay_hours=24, sender_header=from_header)
                            sent_count += 1
                        except Exception as e:
                            st.error(f"Error {s_email} se {target} ko: {e}")
                        
                        p_bar.progress(min(sent_count / total_targets, 1.0))
                        time.sleep(5) # 5 Second ka safe gap
                
                status_text.success("🎉 Pura Batch Complete Ho Gaya! Ab Tab 2 me jaakar Backup Download kar lijiye.")

# ================= TAB 2 : DAY 2 FOLLOW-UPS =================
with tab2:
    st.markdown("### 💾 1. Database Backup & Restore")
    c1, c2 = st.columns(2)
    with c1:
        if os.path.exists(db.DB_NAME):
            with open(db.DB_NAME, "rb") as f:
                st.download_button("📥 Download Backup (Aaj ka kaam save karein)", f, file_name="auto_email_backup.db", mime="application/octet-stream")
    with c2:
        uploaded_db = st.file_uploader("📤 Restore Backup (Kal ka data wapas layein)", type=["db"])
        if uploaded_db:
            if st.button("🔄 Restore Database"):
                with open(db.DB_NAME, "wb") as f:
                    f.write(uploaded_db.getvalue())
                st.success("✅ Database Restore ho gaya! Page ko ek baar refresh karein.")
    
    st.markdown("---")
    st.markdown("### ⚡ 2. Bulk Follow-up Engine")
    st.info("Follow-up bhejne ke liye wahi Senders CSV dobara upload karein taaki tool ko Passwords mil sakein.")
    
    senders_csv_followup = st.file_uploader("📥 Upload Senders CSV (Passwords ke liye)", type=['csv'], key="s2")
    body_day2 = st.text_area("Follow-up Content", height=150, value="Hi,\n\nI wanted to follow up again — please share your feedback.\n\nThanks,")

    if st.button("⚡ Start ALL Follow-ups >>", type="primary"):
        if not senders_csv_followup:
            st.error("❌ Pehle Senders CSV upload karein taaki password mil sakein!")
        else:
            df_senders2 = pd.read_csv(senders_csv_followup)
            # Dictionary banalo {email: password}
            pass_dict = {row['Email'].strip(): str(row['Password']).strip() for _, row in df_senders2.iterrows()}
            name_dict = {row['Email'].strip(): str(row.get('Name', '')).strip() for _, row in df_senders2.iterrows()}

            conn = sqlite3.connect(db.DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, sender_email, recipient, subject, message_id, body, sent_at FROM campaigns WHERE status = 'PENDING'")
            pending = cursor.fetchall()
            conn.close()

            if not pending:
                st.warning("⚠️ Kisi ka follow-up pending nahi hai!")
            else:
                total_pending = len(pending)
                st.info(f"🚀 Total {total_pending} logon ko follow-up bheja ja raha hai...")
                p_bar2 = st.progress(0)
                status_text2 = st.empty()
                
                for idx, row in enumerate(pending):
                    cid, s_email, recipient, subj, initial_msg_id, original_body, sent_at = row
                    
                    if s_email not in pass_dict:
                        st.error(f"⚠️ {s_email} ka password CSV me nahi mila. Isko skip kar rahe hain.")
                        continue
                        
                    s_pass = pass_dict[s_email]
                    s_name = name_dict.get(s_email, '')
                    from_header = f"{s_name} <{s_email}>" if s_name else s_email
                    
                    status_text2.text(f"⏳ Followup ja raha hai: {s_email} -> {recipient}")
                    try:
                        sender.send_smtp_message(
                            s_email=s_email, s_pass=s_pass, recipient=recipient, subject=subj,
                            followup_body=body_day2, original_body=original_body, sent_at=sent_at,
                            reply_to_id=initial_msg_id, sender_header=from_header
                        )
                        db.mark_followup_complete(cid)
                    except Exception as e:
                        st.error(f"Error {recipient}: {e}")
                    
                    p_bar2.progress((idx + 1) / total_pending)
                    time.sleep(5) # 5 Second Gap
                
                status_text2.success("🎉 Sabhi Follow-ups Done!")
