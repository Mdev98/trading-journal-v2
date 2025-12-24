import secrets
import time
import os
from fastapi import Request, HTTPException, status, Response, Depends
from hashlib import sha256

# Mot de passe owner (hashé, stocké en variable d’environnement)
OWNER_PASSWORD_HASH = os.getenv("OWNER_PASSWORD_HASH")
SESSIONS = {}
SESSION_DURATION = 30 * 60  # 30 minutes

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

def owner_login(password: str, response: Response):
    if not OWNER_PASSWORD_HASH:
        raise HTTPException(status_code=500, detail="Mot de passe owner non configuré.")
    hash_input = hash_password(password)
    if hash_input != OWNER_PASSWORD_HASH:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect.")
    session_id = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + SESSION_DURATION
    SESSIONS[session_id] = expires_at
    # Déterminer si secure doit être True (prod) ou False (dev)
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    is_secure = base_url.startswith("https://")
    # En production (https), secure=True et samesite='none' (cross-site)
    # En local, secure=False et samesite='lax'
    samesite = "none" 
    secure = True 
    response.set_cookie(
        key="owner_session",
        value=session_id,
        httponly=True,
        max_age=SESSION_DURATION,
        samesite=samesite,
        secure=secure
    )
    return {"message": "Authentifié comme owner", "expires_in": SESSION_DURATION}

def verify_owner(request: Request):
    session_id = request.cookies.get("owner_session")
    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Accès owner requis.")
    if SESSIONS[session_id] < int(time.time()):
        del SESSIONS[session_id]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session owner expirée.")
    return True
