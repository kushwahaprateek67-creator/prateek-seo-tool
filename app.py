import streamlit as st
import pandas as pd
import math
import sender
import time
import re

st.set_page_config(page_title="Bulk Auto Engine", layout="wide")

# ================= HACKER DARK THEME =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Fira Code', monospace !important; background-color: #07090e !important; color: #00ff66 !important; }
.stApp { background: radial-gradient(circle at 50% 0%, #0d1912 0%, #050807 100%) !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { background-color: #0b110e !important; color: #00ffaa !important; border: 1px solid #00ff66 !important; }
.stButton > button { background-color: #0d2015 !important; color: #00ff66 !important; border: 1px solid #00ff66 !important; font-weight: 700 !important; }
.stButton > button:hover { background-color: #00ff66 !important; color: #050807 !important; box-shadow: 0 0 20px rgba(0, 255, 102, 0.8) !important; }
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

st.markdown("# ⚡ Bulk Auto Engine (No DB / Stateless)")
st.caption("Upload same files on Day 1 and Day 2. Tool will auto-match Senders to Targets.")

# Global Inputs (Dono din kaam aayenge)
global_sender_name = st.text_input("Sender Name (Sabhi emails is naam se jayenge)", placeholder="Prateek Kushwaha")
subject_input = st.text_input("Email Subject", value="Quick Inquiry")

st.markdown("### 📥 Upload Lists (CSV)")
st.info("Senders CSV me sirf 2 column: 'Email', 'Password'. Targets CSV me 1 column: 'Target_Email'.")

col1, col2 = st.columns(2)
with col1:
    senders_csv = st.file_uploader("1. Senders CSV (e.g. 100 Gmails)", type=['csv'])
with col2:
    targets_csv = st.file_uploader("2. Targets CSV (e.g. 2500 Targets)", type=['csv'])

tab1, tab2 = st.tabs(["🚀 Day 1: Send New Emails", "⚡ Day 2: Send Quoted Follow-ups"])

# ================= TAB 1 : DAY 1 SENDING =================
with tab1:
    body_day1 = st.text_area("Day 1 Email Content", height=150, key="b1")
    
    if st.button("🚀 Start Day 1 Sending >>", type="primary"):
        if not senders_csv or not targets_csv or not body_day1:
            st.error("❌ CSV files upload karein aur Content likhein!")
        else:
            df_senders = pd.read_csv(senders_csv)
            df_targets = pd.read_csv(targets_csv)
            
            senders_list = df_senders.to_dict('records')
            targets_list = [t.strip() for t in df_targets['Target_Email'].dropna().tolist() if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', t.strip())]
            
            chunk_size = math.ceil(len(targets_list) / len(senders_list))
            st.success(f"✅ Total {len(senders_list)} Senders aur {len(targets_list)} Targets. Har Sender {chunk_size} email bhejega.")
            
            p_bar = st.progress(0)
            status = st.empty()
            
            sent_counter = 0
            for i, s_data in enumerate(senders_list):
                s_email = str(s_data['Email']).strip()
                s_pass = str(s_data['Password']).strip()
                
                start_idx = i * chunk_size
                my_targets = targets_list[start_idx : start_idx + chunk_size]
                
                for target in my_targets:
                    status.text(f"⏳ Sending... {s_email} -> {target}")
                    success, err = sender.send_email_direct(s_email, s_pass, target, subject_input, body_day1, global_sender_name)
                    if not success:
                        st.error(f"Error {s_email} to {target}: {err}")
                    
                    sent_counter += 1
                    p_bar.progress(min(sent_counter / len(targets_list), 1.0))
                    time.sleep(5) # 5 seconds gap
            
            status.success("🎉 Day 1 Sending Complete!")

# ================= TAB 2 : DAY 2 FOLLOW-UPS =================
with tab2:
    st.warning("⚠️ Day 2 me wahi CSV files upload karein jo Day 1 me ki thi. Tool automatically wahi setting banayega.")
    
    body_day2_new = st.text_area("Naya Follow-up Message", value="Hi,\n\nJust following up on my previous email.", height=100)
    body_day2_old = st.text_area("Purana Message (Neeche Quote karne ke liye)", placeholder="Day 1 ka content yahan daalein...", height=100)
    
    if st.button("⚡ Start Quoted Follow-ups >>", type="primary"):
        if not senders_csv or not targets_csv or not body_day2_old:
            st.error("❌ CSV files upload karein aur purana message dalein!")
        else:
            # Same math logic as Day 1
            df_senders = pd.read_csv(senders_csv)
            df_targets = pd.read_csv(targets_csv)
            
            senders_list = df_senders.to_dict('records')
            targets_list = [t.strip() for t in df_targets['Target_Email'].dropna().tolist() if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', t.strip())]
            
            chunk_size = math.ceil(len(targets_list) / len(senders_list))
            
            p_bar2 = st.progress(0)
            status2 = st.empty()
            
            sent_counter2 = 0
            for i, s_data in enumerate(senders_list):
                s_email = str(s_data['Email']).strip()
                s_pass = str(s_data['Password']).strip()
                
                start_idx = i * chunk_size
                my_targets = targets_list[start_idx : start_idx + chunk_size]
                
                for target in my_targets:
                    # Gmail automatically threads emails if Subject starts with 'Re: ' and matches the original
                    followup_subj = subject_input if subject_input.lower().startswith("re:") else f"Re: {subject_input}"
                    
                    # Create quoted body
                    full_followup_body = (
                        f"{body_day2_new}\n\n"
                        f"--------------------------------------------------\n"
                        f"From: {global_sender_name} <{s_email}>\n"
                        f"To: {target}\n"
                        f"Subject: {subject_input}\n\n"
                        f"{body_day2_old}"
                    )
                    
                    status2.text(f"⏳ Follow-up... {s_email} -> {target}")
                    success, err = sender.send_email_direct(s_email, s_pass, target, followup_subj, full_followup_body, global_sender_name)
                    if not success:
                        st.error(f"Error {s_email} to {target}: {err}")
                    
                    sent_counter2 += 1
                    p_bar2.progress(min(sent_counter2 / len(targets_list), 1.0))
                    time.sleep(5)
            
            status2.success("🎉 Sabhi Follow-ups Done! Threading automatically ho jayegi.")
