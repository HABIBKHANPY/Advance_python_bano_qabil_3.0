import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

def fetch_orders():
    url = 'https://api.sheety.co/'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        orders_lists = data.get('marksheet', [])
        return orders_lists
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
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

    today = datetime.now()
    reminder_days = 1  # Number of days before the event to send a notification
    for event in events:
        event_date = datetime.strptime(event.get('date'), '%Y-%m-%d')
        if today + timedelta(days=reminder_days) == event_date.date():
            user_email = event.get('email')
            event_name = event.get('event_name')
            subject = f"Reminder: Upcoming Event - {event_name}"
            body = f"Dear User,\n\nThis is a reminder for the upcoming event '{event_name}' scheduled for {event_date.date()}.\n\nBest Regards,\nYour Event Notification System"
            send_email(subject, body, user_email)

if __name__ == "__main__":
    notify_upcoming_events()
