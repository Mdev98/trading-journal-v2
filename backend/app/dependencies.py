import time
import os
from fastapi import Request, HTTPException, status
from hashlib import sha256
import jwt

OWNER_PASSWORD_HASH = os.getenv("OWNER_PASSWORD_HASH")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey")
JWT_ALGO = "HS256"
SESSION_DURATION = 30 * 60  # 30 minutes

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

def owner_login(password: str):
    if not OWNER_PASSWORD_HASH:
        raise HTTPException(status_code=500, detail="Mot de passe owner non configuré.")
    hash_input = hash_password(password)
    if hash_input != OWNER_PASSWORD_HASH:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect.")
    payload = {
        "sub": "owner",
        "exp": int(time.time()) + SESSION_DURATION
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
    return {"access_token": token, "token_type": "bearer", "expires_in": SESSION_DURATION}

def verify_owner(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Accès owner requis.")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        if payload.get("sub") != "owner":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session owner expirée.")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token owner invalide.")
    return True
