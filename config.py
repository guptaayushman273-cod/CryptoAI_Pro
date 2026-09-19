import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("COINDCX_KEY")
API_SECRET = os.getenv("COINDCX_SECRET")

BASE_URL = "https://api.coindcx.com"
