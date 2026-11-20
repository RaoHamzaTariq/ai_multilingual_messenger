import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

def get_real_token(email: str, password: str):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "password": password
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        if response.status_code == 200:
            token = data.get("access_token")
            user_id = data.get("user", {}).get("id")
            print("\n================== YOUR REAL SUPABASE JWT TOKEN ==================")
            print(f"User ID: {user_id}")
            print(f"\nAuthorization Header Value to paste in Swagger:\nBearer {token}")
            print("==================================================================\n")
        else:
            print("Error signing in:", data.get("error_description") or data.get("msg") or data)
    except Exception as e:
        print("Failed to connect to Supabase Auth:", e)

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else input("Enter your Supabase email: ")
    password = sys.argv[2] if len(sys.argv) > 2 else input("Enter your password: ")
    get_real_token(email, password)
