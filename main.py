import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Function to fetch orders
def fetch_orders():
    url = 'https://api.sheety.co/aade571b3b1ec122a324d95e3445bebe/marksheet/marksheet'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('marksheet', [])
    except requests.RequestException as e:
        print(f"Failed to fetch data. Error: {e}")
        return None

def send_email(subject, body, to_email):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'your-email@gmail.com'
    smtp_password = 'your-email-password'
    
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")

def notify_upcoming_events():
    events = fetch_orders()
    if not events:
        return

    today = datetime.now().date()
    reminder_days = 1
    for event in events:
        event_date_str = event.get('date')
        if not event_date_str:
            continue
        
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        except ValueError:
            print(f"Date format error: {event_date_str}")
            continue
        
        if today + timedelta(days=reminder_days) == event_date:
            user_email = event.get('email')
            if not user_email:
                continue
            
            event_name = event.get('event_name', 'Unknown Event')
            subject = f"Reminder: Upcoming Event - {event_name}"
            body = (f"Dear User,\n\nThis is a reminder for the upcoming event '{event_name}' "
                    f"scheduled for {event_date}.\n\nBest Regards,\nYour Event Notification System")
            send_email(subject, body, user_email)

if __name__ == "__main__":
    notify_upcoming_events()
