import streamlit as st
import pandas as pd
import math
import sender
import time
import re

st.set_page_config(page_title="Bulk Auto Engine", layout="wide")

# ================= DARK THEME =================
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

st.markdown("# ⚡ Bulk Auto Engine (Resume & Stateless)")
st.caption("Upload same files on Day 1 and Day 2. Connection safe with Skip feature!")

def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

global_sender_name = st.text_input("Sender Name (Sabhi emails is naam se jayenge)", placeholder="Prateek Kushwaha")
subject_input = st.text_input("Email Subject", value="Quick Inquiry")

st.markdown("### 📥 Upload Lists (.xlsx ya .csv)")
col1, col2 = st.columns(2)
with col1:
    senders_file = st.file_uploader("1. Senders File (Col 1: Email, Col 2: Password)", type=['csv', 'xlsx'])
with col2:
    targets_file = st.file_uploader("2. Targets File (Sirf 1 column chahiye)", type=['csv', 'xlsx'])

tab1, tab2 = st.tabs(["🚀 Day 1: Send New Emails", "⚡ Day 2: Send Quoted Follow-ups"])

# ================= TAB 1 : DAY 1 SENDING =================
with tab1:
    body_day1 = st.text_area("Day 1 Email Content", height=150, key="b1")
    
    st.markdown("---")
    skip_targets_d1 = st.number_input("Kitne Day 1 emails ja chuke the? (Pehli baar hai toh 0)", min_value=0, value=0, step=1, key="skip_d1")
    
    if st.button("🚀 Start Day 1 Sending >>", type="primary"):
        if not senders_file or not targets_file or not body_day1:
            st.error("❌ Files upload karein aur Content likhein!")
        else:
            df_senders = load_data(senders_file)
            df_targets = load_data(targets_file)
            
            if len(df_senders.columns) < 2:
                st.error("❌ Senders file me kam se kam 2 columns hone zaroori hain!")
            else:
                s_emails = df_senders.iloc[:, 0].astype(str).tolist()
                s_passes = df_senders.iloc[:, 1].astype(str).tolist()
                senders_list = [{'Email': e.strip(), 'Password': p.strip()} for e, p in zip(s_emails, s_passes) if e.strip() != 'nan' and '@' in e]
                
                targets_list = [str(t).strip() for t in df_targets.iloc[:, 0].dropna().tolist() if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(t).strip())]
                
                if not senders_list or not targets_list:
                    st.error("❌ Files me valid Emails nahi mile.")
                else:
                    chunk_size = math.ceil(len(targets_list) / len(senders_list))
                    st.success(f"✅ Total {len(senders_list)} Senders aur {len(targets_list)} Targets. Har Sender {chunk_size} email bhejega.")
                    
                    p_bar = st.progress(0)
                    status = st.empty()
                    
                    sent_counter = 0
                    global_target_idx = 0
                    
                    for i, s_data in enumerate(senders_list):
                        s_email = s_data['Email']
                        s_pass = s_data['Password']
                        
                        start_idx = i * chunk_size
                        my_targets = targets_list[start_idx : start_idx + chunk_size]
                        
                        for target in my_targets:
                            if global_target_idx < skip_targets_d1:
                                global_target_idx += 1
                                p_bar.progress(min(global_target_idx / len(targets_list), 1.0))
                                continue
                                
                            status.text(f"⏳ Sending... {global_target_idx + 1}/{len(targets_list)} | {s_email} -> {target}")
                            success, err = sender.send_email_direct(s_email, s_pass, target, subject_input, body_day1, global_sender_name)
                            
                            if not success:
                                st.error(f"Error {s_email} to {target}: {err}")
                            
                            sent_counter += 1
                            global_target_idx += 1
                            p_bar.progress(min(global_target_idx / len(targets_list), 1.0))
                            time.sleep(5) 
                    
                    if sent_counter > 0 or skip_targets_d1 > 0:
                        status.success("🎉 Day 1 Sending Complete!")

# ================= TAB 2 : DAY 2 FOLLOW-UPS =================
with tab2:
    st.warning("⚠️ Day 2 me wahi files upload karein jo Day 1 me ki thi.")
    
    body_day2_new = st.text_area("Naya Follow-up Message", value="Hi,\n\nJust following up on my previous email.", height=100)
    body_day2_old = st.text_area("Purana Message (Neeche Quote karne ke liye)", placeholder="Day 1 ka content yahan daalein...", height=100)
    
    st.markdown("---")
    skip_targets_d2 = st.number_input("Kitne Day 2 follow-ups ja chuke the? (Pehli baar hai toh 0)", min_value=0, value=0, step=1, key="skip_d2")
    
    if st.button("⚡ Start Quoted Follow-ups >>", type="primary"):
        if not senders_file or not targets_file or not body_day2_old:
            st.error("❌ Files upload karein aur purana message dalein!")
        else:
            df_senders = load_data(senders_file)
            df_targets = load_data(targets_file)
            
            if len(df_senders.columns) < 2:
                st.error("❌ Senders file me kam se kam 2 columns hone zaroori hain!")
            else:
                s_emails = df_senders.iloc[:, 0].astype(str).tolist()
                s_passes = df_senders.iloc[:, 1].astype(str).tolist()
                senders_list = [{'Email': e.strip(), 'Password': p.strip()} for e, p in zip(s_emails, s_passes) if e.strip() != 'nan' and '@' in e]
                
                targets_list = [str(t).strip() for t in df_targets.iloc[:, 0].dropna().tolist() if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(t).strip())]
                
                if not senders_list or not targets_list:
                    st.error("❌ Files me valid Emails nahi mile.")
                else:
                    chunk_size = math.ceil(len(targets_list) / len(senders_list))
                    
                    p_bar2 = st.progress(0)
                    status2 = st.empty()
                    
                    sent_counter2 = 0
                    global_target_idx2 = 0
                    
                    for i, s_data in enumerate(senders_list):
                        s_email = s_data['Email']
                        s_pass = s_data['Password']
                        
                        start_idx = i * chunk_size
                        my_targets = targets_list[start_idx : start_idx + chunk_size]
                        
                        for target in my_targets:
                            if global_target_idx2 < skip_targets_d2:
                                global_target_idx2 += 1
                                p_bar2.progress(min(global_target_idx2 / len(targets_list), 1.0))
                                continue
                                
                            followup_subj = subject_input if subject_input.lower().startswith("re:") else f"Re: {subject_input}"
                            
                            full_followup_body = (
                                f"{body_day2_new}\n\n"
                                f"--------------------------------------------------\n"
                                f"From: {global_sender_name} <{s_email}>\n"
                                f"To: {target}\n"
                                f"Subject: {subject_input}\n\n"
                                f"{body_day2_old}"
                            )
                            
                            status2.text(f"⏳ Follow-up... {global_target_idx2 + 1}/{len(targets_list)} | {s_email} -> {target}")
                            success, err = sender.send_email_direct(s_email, s_pass, target, followup_subj, full_followup_body, global_sender_name)
                            
                            if not success:
                                st.error(f"Error {s_email} to {target}: {err}")
                            
                            sent_counter2 += 1
                            global_target_idx2 += 1
                            p_bar2.progress(min(global_target_idx2 / len(targets_list), 1.0))
                            time.sleep(5)
                    
                    if sent_counter2 > 0 or skip_targets_d2 > 0:
                        status2.success("🎉 Sabhi Follow-ups Done! Threading automatically ho jayegi.")
