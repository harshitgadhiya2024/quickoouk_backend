import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

secreat_key = str(uuid.uuid4())
print(f"{datetime.utcnow()}: Secreat key of quickoo backend: {secreat_key}")

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

constant_dict = {
    "mongo_url": MONGO_URL,
    "secreat_key": secreat_key
}