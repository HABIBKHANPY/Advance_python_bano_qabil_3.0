import os
import datetime
import smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = 'spreadsheet'
SHEET_NAME = 'spreadsheet'
RANGE_NAME = 'A1:E10'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
FROM_EMAIL = 'hk898243gmail.com'
PASSWORD = 'your-password'

def get_google_sheets_service():
    """Set up and return Google Sheets API service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

def fetch_event_data(service):
    """Fetch event data from Google Sheets."""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f'{SHEET_NAME}!{RANGE_NAME}'
    ).execute()
    return result.get('values', [])

def send_email(subject, body, to_email):
    """Send an email notification."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(FROM_EMAIL, PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())

def main():
    """Main function to orchestrate fetching data and sending emails."""
    service = get_google_sheets_service()
    events = fetch_event_data(service)
    
    now = datetime.datetime.now()
    reminder_threshold = now + datetime.timedelta(days=7)
    
    for row in events:
        try:
            event_name = row[0]
            event_date = datetime.datetime.strptime(row[1], '%Y-%m-%d')
            event_time = datetime.datetime.strptime(row[2], '%H:%M').time()
            notification_email = row[3]
            
            event_datetime = datetime.datetime.combine(event_date, event_time)
            
            if event_datetime <= reminder_threshold:
                subject = f'Upcoming Event: {event_name}'
                body = f'Reminder: {event_name} on {event_date.strftime("%Y-%m-%d")} at {event_time.strftime("%H:%M")}'
                send_email(subject, body, notification_email)
        
        except (IndexError, ValueError) as e:
            print(f'Error processing row {row}: {e}')

if __name__ == '__main__':
    main()
