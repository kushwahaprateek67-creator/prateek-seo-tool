import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_direct(s_email, s_pass, recipient, subject, body, sender_name=""):
    msg = MIMEMultipart()
    from_header = f"{sender_name} <{s_email}>" if sender_name else s_email
    
    msg['From'] = from_header
    msg['To'] = recipient
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(s_email, s_pass)
        server.sendmail(s_email, recipient, msg.as_string())
        server.quit()
        return True, ""
    except Exception as e:
        return False, str(e)
