import streamlit as st
import pandas as pd
import db
import sender
import time
import re

st.set_page_config(page_title="Bulk Email Tool", layout="wide")
db.init_db()

st.title("📧 Bulk Email Outreach & Follow-up Tool")

tab1, tab2 = st.tabs(["🚀 Send Bulk Emails (Day 1)", "📊 Tracker & Send Follow-ups"])

with tab1:
    st.subheader("1. Account Setup")
    c1, c2 = st.columns(2)
    with c1:
        s_email = st.text_input("Apna Gmail ID", placeholder="abc@gmail.com")
        s_pass = st.text_input("16-Digit App Password", type="password")
    with c2:
        delay_hrs = st.number_input("Follow-up Delay (Hours)", min_value=0.01, value=24.0, step=0.5)

    st.subheader("2. Target Emails (Ek line mein ek email)")
    email_list_input = st.text_area(
        "30 ya jitne bhi email addresses hain, yahan paste karein:",
        height=180,
        placeholder="client1@example.com\nclient2@example.com\nclient3@example.com"
    )
    
    subject = st.text_input("Email Subject", value="Business Inquiry")
    
    c3, c4 = st.columns(2)
    with c3:
        body_day1 = st.text_area("Day 1 Email Content", height=150, value="Hi,\n\nI wanted to connect regarding your business.")
    with c4:
        body_day2 = st.text_area("Day 2 Follow-up Content", height=150, value="Hi again,\n\nJust following up on my previous email.")

    if st.button("🚀 Send Emails with 4s Delay", type="primary"):
        if not s_email or not s_pass:
            st.error("Apna Gmail aur App Password enter karein!")
        elif not email_list_input.strip():
            st.error("Kripya email addresses paste karein!")
        else:
            raw_emails = email_list_input.split('\n')
            valid_emails = []
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            
            for mail in raw_emails:
                clean_mail = mail.strip()
                if clean_mail and re.match(email_pattern, clean_mail):
                    valid_emails.append(clean_mail)

            if not valid_emails:
                st.error("Koi valid email address nahi mila.")
            else:
                total = len(valid_emails)
                st.info(f"Total {total} emails mile hain. Har email ke beech 4 second ka gap rahega...")
                
                progress_bar = st.progress(0)
                status_box = st.empty()
                success_count = 0
                
                for i, recipient in enumerate(valid_emails):
                    status_box.text(f"Sending ({i+1}/{total}) -> {recipient} ...")
                    try:
                        sender.send_day1_email(s_email, s_pass, recipient, subject, body_day1, delay_hours=delay_hrs)
                        success_count += 1
                    except Exception as e:
                        st.error(f"Failed for {recipient}: {e}")
                    
                    progress_bar.progress((i + 1) / total)
                    
                    # Aakhri email ke baad wait karne ki zaroorat nahi hai
                    if i < total - 1:
                        time.sleep(4)
                
                status_box.empty()
                st.success(f"✅ Kaam poora hua! {success_count}/{total} emails 4-4 second ke gap par successfully send ho gaye.")

with tab2:
    st.subheader("Follow-up Engine & Campaign Tracker")
    records = db.get_all_records()
    if records:
        df_records = pd.DataFrame(records, columns=["ID", "Receiver", "Subject", "Sent At", "Follow-up Due", "Status"])
        st.dataframe(df_records, use_container_width=True)
    else:
        st.info("Abhi tak koi email nahi bheja gaya.")

    st.markdown("---")
    st.write("Agle din jab follow-up bhejna ho, yeh button dabayein (is mein bhi 4 second ka delay automatically apply hoga):")
    
    if st.button("Check & Send Due Follow-ups"):
        if not s_email or not s_pass:
            st.error("Pehle Tab 1 mein apna Gmail aur App Password enter karein!")
        else:
            pending = db.get_pending_followups()
            if not pending:
                st.warning("Abhi kisi bhi email ka 24 ghante (due time) pura nahi hua hai.")
            else:
                st.info(f"{len(pending)} emails follow-up ke liye ready hain. Bhejna shuru kar rahe hain...")
                p_bar = st.progress(0)
                f_status = st.empty()
                
                for idx, row in enumerate(pending):
                    cid, recipient, subj, initial_msg_id = row
                    f_status.text(f"Sending follow-up ({idx+1}/{len(pending)}) -> {recipient} ...")
                    try:
                        sender.send_smtp_message(s_email, s_pass, recipient, subj, body_day2, reply_to_id=initial_msg_id)
                        db.mark_followup_complete(cid)
                        st.success(f"✅ Follow-up sent to: {recipient}")
                    except Exception as e:
                        st.error(f"❌ Failed for {recipient}: {e}")
                    
                    p_bar.progress((idx + 1) / len(pending))
                    if idx < len(pending) - 1:
                        time.sleep(4)
                
                f_status.empty()
                st.success("🎉 Sabhi eligible contacts ko follow-up successfully bhej diya gaya!")