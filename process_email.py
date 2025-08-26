# process_email.py
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def draft_response(email_body, subject, sender):
    """
    The CORE of the agent. This function uses the LLM to reason about the email
    and draft a context-aware reply.
    """
    # The system prompt defines the agent's role and personality
    system_prompt = """
    You are a helpful, professional, and concise email assistant. Your task is to analyze the provided email and draft a short, appropriate reply.
    If the email is spam, a newsletter, an out-of-office message, or clearly does not require a response, simply return the exact word 'NO_RESPONSE_NEEDED'.
    """

    # The user prompt provides the specific context for the LLM
    user_prompt = f"""
    **From:** {sender}
    **Subject:** {subject}

    **Email Body:**
    {email_body}

    Please draft a helpful reply to this email. Be professional and direct.
    """

    try:
        # Call the Groq API instead of OpenAI
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",  # Fast and free model from Groq
            temperature=0.7,
            max_tokens=250
        )
        # Extract the generated text from the response
        drafted_reply = chat_completion.choices[0].message.content
        return drafted_reply

    except Exception as e:
        return f"Error generating reply: {e}"