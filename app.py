import streamlit as st
import pandas as pd
import db
import sender
import time
import re

st.set_page_config(page_title="TERMINAL // OUTREACH_OS", layout="wide", initial_sidebar_state="collapsed")

# ================= HACKER CYBERPUNK THEME CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Fira Code', monospace !important;
    background-color: #07090e !important;
    color: #00ff66 !important;
}

/* Background canvas */
.stApp {
    background: radial-gradient(circle at 50% 0%, #0d1912 0%, #050807 100%) !important;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #00ff66 !important;
    text-shadow: 0 0 10px rgba(0, 255, 102, 0.45);
    letter-spacing: 1px;
}

/* Input Fields & Textareas */
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

/* Buttons */
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

/* Tab design */
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

/* Progress bar */
.stProgress > div > div > div > div {
    background-color: #00ff66 !important;
    box-shadow: 0 0 12px #00ff66;
}

/* Terminal Alerts / Boxes */
.stAlert {
    background-color: #0a1410 !important;
    border: 1px solid #00ff66 !important;
    color: #00ffaa !important;
    font-family: 'Fira Code', monospace !important;
}
</style>
""", unsafe_allow_html=True)

# ================= AUTH GATEWAY =================
APP_PASSWORD = "Prateek@2026"  # <-- Apna secret password yahan set karein

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state.get("password_input") == APP_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.error("[-] ACCESS_DENIED: UNAUTHORIZED CREDENTIALS")

if not st.session_state.authenticated:
    st.markdown("### `[SYSTEM LOCKED // ROOT_AUTH_REQUIRED]`")
    st.write("`>> Enter authorization key to access outreach mainframe:`")
    st.text_input("PASSPHRASE", type="password", key="password_input", on_change=check_password)
    st.button("AUTHENTICATE >>", on_click=check_password)
    st.stop()
# ================================================

db.init_db()

st.markdown("# `⚡ TERMINAL // OUTREACH_SYSTEM v2.4`")
st.caption("`STATUS: ONLINE | PROXY: ENCRYPTED | PROTOCOL: SMTP_DIRECT`")

tab1, tab2 = st.tabs(["[1] DISPATCH PROTOCOL", "[2] TELEMETRY & AUTO-FOLLOWUP"])

with tab1:
    st.markdown("### `:: NODE CREDENTIALS ::`")
    c1, c2 = st.columns(2)
    with c1:
        s_email = st.text_input("SENDER_GMAIL", placeholder="target@gmail.com")
        s_pass = st.text_input("APP_AUTH_TOKEN (16-DIGIT)", type="password")
    with c2:
        delay_hrs = st.number_input("FOLLOWUP_LATENCY (HOURS)", min_value=0.01, value=24.0, step=0.5)

    st.markdown("### `:: TARGET MATRIX ::`")
    email_list_input = st.text_area(
        "TARGET_PAYLOADS (1 IP/EMAIL PER LINE)",
        height=180,
        placeholder="target1@domain.com\ntarget2@domain.com\ntarget3@domain.com"
    )
    
    subject = st.text_input("TRANSMISSION_SUBJECT", value="Direct Communication // Priority Node")
    
    c3, c4 = st.columns(2)
    with c3:
        body_day1 = st.text_area("INIT_PAYLOAD [DAY 1]", height=150, value="Establishing secure connection regarding operational synchronization.")
    with c4:
        body_day2 = st.text_area("THREAD_FOLLOWUP [DAY 2]", height=150, value="Following up on transmitted packet. Awaiting response ping.")

    if st.button("EXECUTE TRANSMISSION // 4s INTERVAL >>", type="primary"):
        if not s_email or not s_pass:
            st.error("[-] ERR: SENDER_CREDENTIALS_MISSING")
        elif not email_list_input.strip():
            st.error("[-] ERR: EMPTY_TARGET_BUFFER")
        else:
            raw_emails = email_list_input.split('\n')
            valid_emails = []
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            
            for mail in raw_emails:
                clean_mail = mail.strip()
                if clean_mail and re.match(email_pattern, clean_mail):
                    valid_emails.append(clean_mail)

            if not valid_emails:
                st.error("[-] ERR: NO_VALID_TARGETS_FOUND")
            else:
                total = len(valid_emails)
                st.info(f"[+] INITIATING: {total} targets queued | 4000ms bypass delay active")
                
                progress_bar = st.progress(0)
                status_box = st.empty()
                success_count = 0
                
                for i, recipient in enumerate(valid_emails):
                    status_box.text(f">> DISPATCHING PACKET ({i+1}/{total}) -> {recipient} ...")
                    try:
                        sender.send_day1_email(s_email, s_pass, recipient, subject, body_day1, delay_hours=delay_hrs)
                        success_count += 1
                    except Exception as e:
                        st.error(f"[-] TRANSMISSION_FAILED: {recipient} :: {e}")
                    
                    progress_bar.progress((i + 1) / total)
                    
                    if i < total - 1:
                        time.sleep(4)
                
                status_box.empty()
                st.success(f"[+] MISSION COMPLETE: {success_count}/{total} packets delivered securely.")

with tab2:
    st.markdown("### `:: ACTIVE THREAD TELEMETRY ::`")
    records = db.get_all_records()
    if records:
        df_records = pd.DataFrame(records, columns=["ID", "Receiver", "Subject", "Dispatched At", "Target Ping Due", "Status"])
        st.dataframe(df_records, use_container_width=True)
    else:
        st.info("[i] DATABASE_EMPTY: No telemetry logged.")

    st.markdown("---")
    st.write("`>> Trigger automatic thread injection for eligible packets (4s interval applied):`")
    
    if st.button("DEPLOY ELIGIBLE FOLLOWUPS >>"):
        if not s_email or not s_pass:
            st.error("[-] ERR: ROOT_CREDENTIALS_UNDEFINED_IN_TAB_1")
        else:
            pending = db.get_pending_followups()
            if not pending:
                st.warning("[!] ZERO_PENDING: No nodes have met timeout threshold.")
            else:
                st.info(f"[+] TRIGGERED: Injecting followup to {len(pending)} nodes...")
                p_bar = st.progress(0)
                f_status = st.empty()
                
                for idx, row in enumerate(pending):
                    cid, recipient, subj, initial_msg_id = row
                    f_status.text(f">> INJECTING THREAD ({idx+1}/{len(pending)}) -> {recipient} ...")
                    try:
                        sender.send_smtp_message(s_email, s_pass, recipient, subj, body_day2, reply_to_id=initial_msg_id)
                        db.mark_followup_complete(cid)
                        st.success(f"[+] PACKET_DELIVERED: {recipient}")
                    except Exception as e:
                        st.error(f"[-] FAILED: {recipient} :: {e}")
                    
                    p_bar.progress((idx + 1) / len(pending))
                    if idx < len(pending) - 1:
                        time.sleep(4)
                
                f_status.empty()
                st.success("[+] AUTOMATION_BATCH_CONCLUDED: All nodes updated.")
