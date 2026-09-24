import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid
import db

def send_day1_email(s_email, s_pass, recipient, subject, body, delay_hours=24, sender_header=None):
    msg = MIMEMultipart()
    msg['From'] = sender_header if sender_header else s_email
    msg['To'] = recipient
    msg['Subject'] = subject
    
    msg_id = make_msgid()
    msg['Message-ID'] = msg_id
    
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(s_email, s_pass)
    server.sendmail(s_email, recipient, msg.as_string())
    server.quit()
    
    # Pass delay_hours safely to db
    db.log_initial_email(recipient, subject, message_id=msg_id, due_time_or_hours=delay_hours)

def send_smtp_message(s_email, s_pass, recipient, subject, body, reply_to_id=None, sender_header=None):
    msg = MIMEMultipart()
    msg['From'] = sender_header if sender_header else s_email
    msg['To'] = recipient
    
    if not subject.lower().startswith("re:"):
        msg['Subject'] = f"Re: {subject}"
    else:
        msg['Subject'] = subject
        
    if reply_to_id:
        msg['In-Reply-To'] = reply_to_id
        msg['References'] = reply_to_id
        
    msg.attach(MIMEText(body, 'plain'))
    
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(s_email, s_pass)
    server.sendmail(s_email, recipient, msg.as_string())
    server.quit()
