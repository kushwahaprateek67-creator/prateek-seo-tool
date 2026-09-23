import streamlit as st
import pandas as pd
import db
import sender
import time
import re

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
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background-color: #0b110e !important;
    color: #00ffaa !important;
    border: 1px solid #00ff66 !important;
    border-radius: 4px !important;
    font-family: 'Fira Code', monospace !important;
    box-shadow: 0 0 6px rgba(0, 255, 102, 0.2);
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #00ffcc !important;
    box-shadow: 0 0 14px rgba(0, 255, 204, 0.5) !important;
}

.stButton > button {
    background-color: #0d2015 !important;
    color: #00ff66 !important;
    border: 1px solid #00ff66 !important;
    border-radius: 4px !important;
    font-family: 'Fira Code', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 1px;
    box-shadow: 0 0 10px rgba(0, 255, 102, 0.3) !important;
    transition: all 0.25s ease-in-out;
}

.stButton > button:hover {
    background-color: #00ff66 !important;
    color: #050807 !important;
    box-shadow: 0 0 20px rgba(0, 255, 102, 0.8) !important;
}

button[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #4ade80 !important;
    font-family: 'Fira Code', monospace !important;
    border-bottom: 2px solid #143521 !important;
}

button[aria-selected="true"] {
    color: #00ff66 !important;
    border-bottom: 2px solid #00ff66 !important;
    text-shadow: 0 0 8px #00ff66;
}

.stProgress > div > div > div > div {
    background-color: #00ff66 !important;
    box-shadow: 0 0 12px #00ff66;
}

.stAlert {
    background-color: #0a1410 !important;
    border: 1px solid #00ff66 !important;
    color: #00ffaa !important;
    font-family: 'Fira Code', monospace !important;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN GATEWAY =================
APP_PASSWORD = "Prateek@2026"  # <-- Password badalna ho toh yahan badlein

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.get("password_input") == APP_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.error("❌ Galat Password! Dobara koshish karein.")

if not st.session_state.authenticated:
    st.markdown("### 🔒 Tool Login")
    st.write("Is tool ko access karne ke liye password enter karein:")
    st.text_input("Enter Password", type="password", key="password_input", on_change=check_password)
    st.button("Login >>", on_click=check_password)
    st.stop()
# ================================================

db.init_db()

st.markdown("# ⚡ Bulk Email Outreach Tool")
st.caption("Active Status: Online | Delay: 4 Seconds")

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

    delay_hrs = st.number_input("Follow-up Delay Time (Ghante)", min_value=0.01, value=24.0, step=0.5)

    st.markdown("### 2. Target Email List")
    email_list_input = st.text_area(
        "Jinhe email bhejna hai (Ek line mein ek email dalein):",
        height=180,
        placeholder="client1@gmail.com\nclient2@gmail.com\nclient3@gmail.com"
    )
    
    subject = st.text_input("Email Subject", value="Quick Inquiry")
    
    c4, c5 = st.columns(2)
    with c4:
        body_day1 = st.text_area("Day 1 Email Content", height=150, value="Hi,\n\nI hope you are doing well.\n\nBest regards,")
    with c5:
        body_day2 = st.text_area("Day 2 Follow-up Content", height=150, value="Hi,\n\nJust following up on my previous email.\n\nBest regards,")

    if st.button("🚀 Send Emails (4s Delay) >>", type="primary"):
        if not s_email or not s_pass:
            st.error("❌ Kripya apna Gmail aur 16-digit App Password bharein!")
        elif not email_list_input.strip():
            st.error("❌ Email list khaali hai! Kripya target emails paste karein.")
        else:
            raw_emails = email_list_input.split('\n')
            valid_emails = []
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            
            for mail in raw_emails:
                clean_mail = mail.strip()
                if clean_mail and re.match(email_pattern, clean_mail):
                    valid_emails.append(clean_mail)

            if not valid_emails:
                st.error("❌ Koi valid email address nahi mila.")
            else:
                total = len(valid_emails)
                st.info(f"✅ Total {total} emails mile. Har email ke beech 4 second ka gap rahega...")
                
                progress_bar = st.progress(0)
                status_box = st.empty()
                success_count = 0
                
                # Format sender address with name if provided
                from_header = f"{sender_name} <{s_email}>" if sender_name.strip() else s_email

                for i, recipient in enumerate(valid_emails):
                    status_box.text(f"Bhej rahe hain ({i+1}/{total}) -> {recipient} ...")
                    try:
                        sender.send_day1_email(s_email, s_pass, recipient, subject, body_day1, delay_hours=delay_hrs, sender_header=from_header)
                        success_count += 1
                    except TypeError:
                        # Fallback agar sender.py mein sender_header argument na ho
                        sender.send_day1_email(s_email, s_pass, recipient, subject, body_day1, delay_hours=delay_hrs)
                        success_count += 1
                    except Exception as e:
                        st.error(f"❌ Error for {recipient}: {e}")
                    
                    progress_bar.progress((i + 1) / total)
                    
                    if i < total - 1:
                        time.sleep(4)
                
                status_box.empty()
                st.success(f"🎉 Kaam poora hua! {success_count}/{total} emails successfully chale gaye.")

with tab2:
    st.markdown("### 📊 Email History aur Follow-up Status")
    records = db.get_all_records()
    if records:
        df_records = pd.DataFrame(records, columns=["ID", "Receiver Email", "Subject", "Sent Time", "Follow-up Due Time", "Status"])
        st.dataframe(df_records, use_container_width=True)
    else:
        st.info("Abhi tak koi email record nahi hai.")

    st.markdown("---")
    st.write("Jin emails ka due time pura ho gaya hai, unhe follow-up bhejne ke liye click karein:")
    
    if st.button("Bhejo Due Follow-ups >>"):
        if not s_email or not s_pass:
            st.error("❌ Pehle Tab 1 mein jakar apna Gmail aur App Password enter karein!")
        else:
            pending = db.get_pending_followups()
            if not pending:
                st.warning("⚠️ Abhi kisi bhi email ka due time pura nahi hua hai.")
            else:
                st.info(f"{len(pending)} emails follow-up ke liye ready hain...")
                p_bar = st.progress(0)
                f_status = st.empty()
                from_header = f"{sender_name} <{s_email}>" if sender_name.strip() else s_email
                
                for idx, row in enumerate(pending):
                    cid, recipient, subj, initial_msg_id = row
                    f_status.text(f"Follow-up bhej rahe hain ({idx+1}/{len(pending)}) -> {recipient} ...")
                    try:
                        sender.send_smtp_message(s_email, s_pass, recipient, subj, body_day2, reply_to_id=initial_msg_id, sender_header=from_header)
                        db.mark_followup_complete(cid)
                        st.success(f"✅ Follow-up send: {recipient}")
                    except TypeError:
                        sender.send_smtp_message(s_email, s_pass, recipient, subj, body_day2, reply_to_id=initial_msg_id)
                        db.mark_followup_complete(cid)
                        st.success(f"✅ Follow-up send: {recipient}")
                    except Exception as e:
                        st.error(f"❌ Error: {recipient} :: {e}")
                    
                    p_bar.progress((idx + 1) / len(pending))
                    if idx < len(pending) - 1:
                        time.sleep(4)
                
                f_status.empty()
                st.success("🎉 Sabhi follow-ups successfully send ho gaye!")
