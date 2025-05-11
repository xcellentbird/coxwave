from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4.1-mini"
OPENAI_TEXT_EMBEDDING_MODEL = "text-embedding-3-small"

DB_PATH = "datas/final_result.db"

COLLECTION_NAME = "smartstore_faq"
