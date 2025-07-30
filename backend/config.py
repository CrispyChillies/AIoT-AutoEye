import os
from dotenv import load_dotenv

load_dotenv()

# Simple configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "autoeye_db"
DEBUG = True
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
VALID_STATUSES = ["light", "moderate", "heavy", "unknown"]
