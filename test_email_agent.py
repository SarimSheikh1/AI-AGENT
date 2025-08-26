# test_email_agent.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def simulate_fetch_email():
    """
    Simulates fetching a new email from the inbox.
    Replace this function with real Gmail API code later.
    """
    simulated_email = {
        'id': 'test_email_123',
        'from': 'colleague@company.com',
        'subject': 'Question about the Q3 Project Report',
        'body': """Hi there,

I hope you're having a productive week.

I'm working on the final review for the Q3 Project Report and had a quick question about the data in Section 2. The figures seem a bit lower than our initial forecasts. Could you provide a brief explanation or point me to the notes on that?

No huge rush, but by tomorrow EOD would be great.

Thanks,

Alex
"""
    }
    return simulated_email

def ai_draft_reply(email_body, email_subject, email_from):
    """
    The CORE of the agent. This function uses the LLM to reason about the email
    and draft a context-aware reply.
    """
    # The system prompt defines the agent's role and personality
    system_prompt = """
    You are a helpful, professional, and concise email assistant. Your task is to analyze the provided email and draft a short, appropriate reply.
    If the email is spam, a newsletter, an out-of-office message, or clearly does not require a response, simply return the word 'IGNORE'.
    """

    # The user prompt provides the specific context for the LLM
    user_prompt = f"""
    **From:** {email_from}
    **Subject:** {email_subject}

    **Email Body:**
    {email_body}

    Please draft a helpful reply to this email. Be professional and direct.
    """

    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can use "gpt-4o" for more power, or "gpt-3.5-turbo" for cheaper testing
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,  # Controls creativity. 0.7 is a good balance for creative yet focused replies.
            max_tokens=250    # Limits the length of the response.
        )
        # Extract the generated text from the response
        drafted_reply = response.choices[0].message.content
        return drafted_reply

    except Exception as e:
        return f"Error generating reply: {e}"

def main():
    """
    Main function to run the test agent loop.
    """
    print("🤖 AI Email Agent Test Script Started...")
    print("Simulating a new email arrival...\n")

    # Step 1: Perceive - Get the email
    email = simulate_fetch_email()
    print(f"📧 **Simulated Email Received**")
    print(f"From: {email['from']}")
    print(f"Subject: {email['subject']}")
    print(f"Body:\n{email['body']}\n")
    print("-" * 50)

    # Step 2: Reason - Let the AI draft a reply
    print("🧠 **AI is drafting a reply...**")
    ai_reply = ai_draft_reply(email['body'], email['subject'], email['from'])

    # Step 3: Act (Simulated) - Print the action the agent would take
    print("✅ **Reply Drafted Successfully!**\n")
    if "IGNORE" in ai_reply:
        print("🤖 Agent Decision: This email does not require a response (e.g., spam, newsletter).")
    else:
        print("🤖 Agent Decision: A response is needed. The drafted reply is:")
        print("\n--- START OF DRAFT ---")
        print(ai_reply)
        print("--- END OF DRAFT ---\n")
        # In a real agent, you would call send_email() here.

    print("\nTest completed. This was a simulation. No email was actually sent.")

if __name__ == "__main__":
    main()