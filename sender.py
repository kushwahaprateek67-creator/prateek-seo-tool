import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from datetime import datetime, timedelta
import db

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def send_smtp_message(sender_email, app_password, to_email, subject, body, reply_to_id=None):
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.set_content(body)

    new_msg_id = make_msgid()
    msg['Message-ID'] = new_msg_id

    if reply_to_id:
        msg['Subject'] = f"Re: {subject}"
        msg['In-Reply-To'] = reply_to_id
        msg['References'] = reply_to_id
    else:
        msg['Subject'] = subject

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(sender_email, app_password.replace(" ", ""))
        server.send_message(msg)

    return new_msg_id

def send_day1_email(sender_email, app_password, recipient, subject, body, delay_hours=24):
    msg_id = send_smtp_message(sender_email, app_password, recipient, subject, body)
    due_time = datetime.now() + timedelta(hours=delay_hours)
    db.log_initial_email(recipient, subject, msg_id, due_time)
    return msg_id

def process_followups(sender_email, app_password, followup_body):
    pending = db.get_pending_followups()
    results = []
    
    for row in pending:
        cid, recipient, subject, initial_msg_id = row
        try:
            send_smtp_message(sender_email, app_password, recipient, subject, followup_body, reply_to_id=initial_msg_id)
            db.mark_followup_complete(cid)
            results.append((recipient, "Success"))
        except Exception as e:
            results.append((recipient, f"Failed: {e}"))
            
    return results