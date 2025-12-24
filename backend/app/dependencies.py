import os
from fastapi import Header, HTTPException, status, Depends
from fastapi.security.utils import get_authorization_scheme_param
from hashlib import sha256

from app.main import API_KEY_HASH

def verify_api_key(x_api_key: str = Header(...)):
    if not API_KEY_HASH:
        raise HTTPException(status_code=500, detail="API key non configurée.")
    # On hash la clé reçue pour comparer
    hashed = sha256(x_api_key.encode()).hexdigest()
    if hashed != API_KEY_HASH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide.",
        )
    return True
