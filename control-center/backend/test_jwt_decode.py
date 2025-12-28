"""Test JWT token decoding"""
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

# Token from login response
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2MjgyNjg2MywiaWF0IjoxNzYyNzQwNDYzLCJ0eXBlIjoiYWNjZXNzIn0.AW0h9zf0zcVJrHfJEry8ueZanwB8Xw4QMk75Qo7lkOI"

print(f"JWT_SECRET: {JWT_SECRET[:20]}...")
print(f"Token: {token[:50]}...")

try:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    print("\nToken decoded successfully!")
    print(f"Payload: {payload}")
except jwt.ExpiredSignatureError:
    print("\nERROR: Token has expired")
except jwt.InvalidTokenError as e:
    print(f"\nERROR: Invalid token: {e}")
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
