from langchain_google_genai import ChatGoogleGenerativeAI
import os
import dotenv
dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key = GEMINI_API_KEY,
    temperature=0.3
)