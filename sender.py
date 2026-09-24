import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid
import db

def send_day1_email(s_email, s_pass, recipient, subject, body, delay_hours=24, sender_header=None):
    msg = MIMEMultipart()
    sender_val = sender_header if sender_header else s_email
    msg['From'] = sender_val
    msg['To'] = recipient
    msg['Subject'] = subject
    
    msg_id = make_msgid()
    msg['Message-ID'] = msg_id
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(s_email, s_pass)
    server.sendmail(s_email, recipient, msg.as_string())
    server.quit()
    
    # Body bhi log kar rahe hain taaki follow-up mein quote kar sakein
    db.log_initial_email(recipient, subject, body, message_id=msg_id, due_time_or_hours=delay_hours)

def send_smtp_message(s_email, s_pass, recipient, subject, followup_body, original_body="", sent_at="", reply_to_id=None, sender_header=None):
    msg = MIMEMultipart()
    sender_val = sender_header if sender_header else s_email
    msg['From'] = sender_val
    msg['To'] = recipient
    
    clean_subj = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    msg['Subject'] = clean_subj
        
    if reply_to_id:
        msg['In-Reply-To'] = reply_to_id
        msg['References'] = reply_to_id
        
    # Standard email reply quoted format create karein
    if original_body:
        full_email_content = (
            f"{followup_body}\n\n"
            f"--------------------------------------------------\n"
            f"From: {sender_val}\n"
            f"Sent: {sent_at}\n"
            f"To: {recipient}\n"
            f"Subject: {subject}\n\n"
            f"{original_body}"
        )
    else:
        full_email_content = followup_body

    msg.attach(MIMEText(full_email_content, 'plain'))
    
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(s_email, s_pass)
    server.sendmail(s_email, recipient, msg.as_string())
    server.quit()
