import os
from dotenv import load_dotenv

# Load .env file if it exists, otherwise continue without it
try:
    load_dotenv()
    print("✓ .env file loaded successfully")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

print(f"GOOGLE_API_KEY: {'✓ Set' if GOOGLE_API_KEY else '❌ Not set'}")
print(f"SERPER_API_KEY: {'✓ Set' if SERPER_API_KEY else '❌ Not set'}") 