# send_email.py (UPDATED TO USE GMAIL API)
import base64
from email.mime.text import MIMEText
from fetch_emails import authenticate_gmail  # Reuse the authentication

def create_message(to, subject, message_text):
    """Create a message for an email."""
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(to_address, subject, body):
    """
    Actually sends an email using the Gmail API.
    """
    try:
        service = authenticate_gmail()
        message = create_message(to_address, subject, body)
        
        # Send the message
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        
        print(f"✅ Email successfully sent to {to_address}")
        print(f"Message Id: {sent_message['id']}")
        
    except Exception as error:
        print(f'❌ Failed to send email: {error}')