# fetch_emails.py (REPLACED WITH REAL GMAIL CODE)
import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.json.
# This scope allows reading, sending, and managing emails.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails():
    """
    Fetches real unread emails from your Gmail inbox using the Gmail API.
    Returns a list of email dictionaries with 'id', 'sender', 'subject', and 'body'.
    """
    try:
        service = authenticate_gmail()
        
        # Call the Gmail API to get unread messages
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
        messages = results.get('messages', [])
        
        email_list = []
        
        if not messages:
            print('No unread messages found.')
            return []
        else:
            print(f"Found {len(messages)} unread messages.")
            
            for message in messages:
                msg_id = message['id']
                # Get the full message details
                msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                
                # Extract message body
                if 'parts' in msg['payload']:
                    # For multipart messages
                    parts = msg['payload']['parts']
                    body_data = parts[0]['body']['data']
                else:
                    # For simple messages
                    body_data = msg['payload']['body']['data']
                
                # Decode the base64 URL-safe encoded body
                body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                
                # Clean up the body text (often contains HTML tags)
                # This is a simple cleaner - you might want to improve this
                clean_body = " ".join(body.split())[:500] + "..."  # First 500 chars
                
                email_list.append({
                    'id': msg_id,
                    'sender': sender,
                    'subject': subject,
                    'body': clean_body
                })
                
                # Stop after 5 emails to avoid processing too many at once
                if len(email_list) >= 5:
                    break
        
        return email_list

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []