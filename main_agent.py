# main_agent.py
import time
from fetch_emails import get_unread_emails
from process_email import draft_response
from send_email import send_email

def email_agent_loop():
    """Runs continuously, checking for emails and replying."""
    while True:
        # 1. PERCEIVE: Check inbox for unread emails
        print("🔍 Checking for new emails...")
        unread_emails = get_unread_emails()
        
        if not unread_emails:
            print("No new emails found.")
        else:
            print(f"Found {len(unread_emails)} new email(s).")
        
        for email in unread_emails:
            print(f"\n📧 Processing email from {email['sender']}")
            
            # 2. REASON: Let the LLM draft a response
            ai_response = draft_response(email['body'], email['subject'], email['sender'])
            
            # 3. ACT: If the LLM decides a response is needed, send it.
            if ai_response != "NO_RESPONSE_NEEDED" and "NO_RESPONSE_NEEDED" not in ai_response:
                send_email(
                    to_address=email['sender'],
                    subject=f"Re: {email['subject']}",
                    body=ai_response
                )
                print(f"✅ Replied to {email['sender']}")
            else:
                print(f"❌ No response needed for email from {email['sender']} (Newsletter/Promo).")
            
            # Mark email as read or processed (you'd need to implement this)
            # mark_as_read(email['id'])
        
        # Check every 60 seconds
        print("\n⏳ Sleeping for 60 seconds...\n")
        time.sleep(60)

if __name__ == "__main__":
    email_agent_loop()