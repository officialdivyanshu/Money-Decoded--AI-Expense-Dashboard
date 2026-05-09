import os
from groq import Groq
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("GROQ_API_KEY")

# Initialize client
client = Groq(api_key=api_key)


def generate_insight(text_data):
    prompt = f"""
    You are a financial assistant.

    Based on the following spending data, explain insights in simple human language:

    {text_data}

    Keep it short and clear.
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content