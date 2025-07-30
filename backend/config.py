import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# Simple configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = "autoeye_db"
DEBUG = True
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
VALID_STATUSES = ["light", "moderate", "heavy", "unknown"]


# MQTT configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", None)
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", None)
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "traffic/data")

# Generate unique client ID to avoid conflicts
MQTT_CLIENT_ID = f"autoeye_backend_{uuid.uuid4().hex[:8]}"
