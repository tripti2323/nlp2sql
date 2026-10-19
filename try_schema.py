import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from src.schema import get_schema_text

load_dotenv()
client = genai.Client()
model = os.getenv("GEMINI_MODEL")

schema = get_schema_text()
question = "Which country has the most customers?"

prompt = f"""You are a SQLite expert. Given this database schema, write one SQLite query that answers the question.
Return only the SQL, with no explanation and no markdown.

{schema}

Question: {question}
SQL:"""

response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=types.GenerateContentConfig(temperature=0),
)
print(response.text)