# this script is for checking env variables. Run seperate to main app
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=== Environment Variables Check ===")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY', 'NOT SET')}")
print(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print(f"AWS_ACCESS_KEY_ID: {'SET' if os.getenv('AWS_ACCESS_KEY_ID') else 'NOT SET'}")
print(f"AWS_SECRET_ACCESS_KEY: {'SET' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'NOT SET'}")
print("=====================================")

# Check if .env file exists
if os.path.exists('.env'):
    print("✅ .env file found")
    with open('.env', 'r') as f:
        lines = f.readlines()
    print(f"📝 .env file has {len(lines)} lines")
else:
    print("❌ .env file not found")