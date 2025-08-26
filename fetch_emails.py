# fetch_emails.py (CORRECTED VERSION)
import os
import base64
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Authenticate with Gmail API"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_email_body(message):
    """Extract and clean email body from Gmail API response"""
    try:
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        return soup.get_text()
        
        # Fallback: try to get data directly from payload
        if 'body' in message['payload'] and 'data' in message['payload']['body']:
            body_data = message['payload']['body']['data']
            return base64.urlsafe_b64decode(body_data).decode('utf-8')
        
        return "Could not extract email body content"
    
    except Exception as e:
        return f"Error extracting body: {str(e)}"

def get_unread_emails():
    """
    Fetches real unread emails from your Gmail inbox using the Gmail API.
    Returns a list of email dictionaries with 'id', 'sender', 'subject', and 'body'.
    """
    try:
        service = authenticate_gmail()
        
        # Call the Gmail API to get unread messages
        results = service.users().messages().list(
            userId='me', 
            labelIds=['INBOX', 'UNREAD'],
            maxResults=5  # Limit to 5 emails at a time
        ).execute()
        
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
                msg = service.users().messages().get(
                    userId='me', 
                    id=msg_id, 
                    format='full'
                ).execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                
                # Extract and clean message body
                body = get_email_body(msg)
                clean_body = " ".join(body.split())[:500] + "..."  # First 500 chars
                
                email_list.append({
                    'id': msg_id,
                    'sender': sender,
                    'subject': subject,
                    'body': clean_body
                })
        
        return email_list

    except HttpError as error:
        print(f'Gmail API Error occurred: {error}')
        return []
    except Exception as error:
        print(f'Unexpected error: {error}')
        return []