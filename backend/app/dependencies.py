import time
import os
from fastapi import Request, HTTPException, status, Depends
from hashlib import sha256
import jwt
from sqlalchemy.orm import Session
from app.database import get_db

OWNER_PASSWORD_HASH = os.getenv("OWNER_PASSWORD_HASH")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretjwtkey")
JWT_ALGO = "HS256"
SESSION_DURATION = 30 * 60  # 30 minutes

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

def hash_api_key(key: str) -> str:
    """Hash une clé API"""
    return sha256(key.encode()).hexdigest()

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

def verify_owner(request: Request, db: Session = Depends(get_db)):
    """Vérifie l'accès en utilisant API key OU JWT token"""

    # Vérifier d'abord la clé API
    api_key = request.headers.get("X-API-Key")
    if api_key:
        from app import models
        from datetime import datetime as dt
        hashed_key = hash_api_key(api_key)
        db_key = db.query(models.APIKey).filter(
            models.APIKey.key == hashed_key,
            models.APIKey.is_active == True
        ).first()
        if db_key:
            # Mettre à jour last_used_at
            db_key.last_used_at = dt.utcnow()
            db.commit()
            return True
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé API invalide.")

    # Sinon, vérifier le JWT token
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
