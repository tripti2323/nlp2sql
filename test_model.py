import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # loads GEMINI_API_KEY and GEMINI_MODEL from .env

client = genai.Client()  # picks up GEMINI_API_KEY automatically
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

response = client.models.generate_content(
    model=model,
    contents="Write a SQL query that selects all rows from a table named customers. Return only SQL.",
    config=types.GenerateContentConfig(temperature=0),
)
print(response.text)