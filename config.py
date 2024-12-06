from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Groq API Key (optional, can be replaced with another model)
api_key = os.getenv('API_KEY')

# Model and embedding configuration
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
CHROMA_PATH = './chroma_db'
