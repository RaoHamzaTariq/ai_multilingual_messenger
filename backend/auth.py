import os
from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from dotenv import load_dotenv
from supabase_client import get_supabase_client

load_dotenv()

# Enables Swagger UI's built-in "Authorize" button and automatic header injection
security = HTTPBearer(auto_error=False)

def verify_jwt_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Extracts and strictly verifies the Supabase access token using environment credentials.
    Supports both HS256 (project JWT secret) and ES256 (Supabase Auth verification).
    Returns the verified user_id.
    """
    token: Optional[str] = None

    if credentials and credentials.credentials:
        token = credentials.credentials
    elif authorization:
        if authorization.startswith("Bearer "):
            token = authorization.split("Bearer ")[1].strip()
        else:
            token = authorization.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Please provide 'Bearer <token>'"
        )

    secret = os.getenv("SUPABASE_JWT_SECRET", "")

    # 1. Attempt HS256 decode if secret is provided
    if secret:
        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            user_id = payload.get("sub")
            if user_id:
                return user_id
        except Exception:
            pass  # Fall through to Supabase client verification

    # 2. Verify with Supabase Auth service (supports ES256 & all token formats)
    try:
        client = get_supabase_client()
        user_res = client.auth.get_user(token)
        if user_res and user_res.user and user_res.user.id:
            return user_res.user.id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired Supabase token: {str(e)}"
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials with Supabase Auth."
    )
