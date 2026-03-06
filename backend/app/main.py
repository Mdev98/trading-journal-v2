"""
Trading Journal API - Point d'entrée principal
Application FastAPI pour le suivi et l'analyse des trades
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
load_dotenv()

# Lecture de la clé API depuis les variables d'environnement
API_KEY_HASH = os.getenv("OWNER_PASSWORD_HASH")


from app.database import engine, Base, get_db
from app.routes import trades, stats, uploads
from fastapi import Response, Request, Depends, Form, HTTPException, status
from app.dependencies import owner_login, verify_owner, hash_api_key
from app import models
from app.schemas import APIKeyCreate, APIKeyWithSecret, APIKeyResponse
import secrets
from sqlalchemy.orm import Session

# Création des tables au démarrage
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Trading Journal API",
    description="API pour journal de trading avec statistiques automatisées",
    version="1.0.0"
)

# Configuration CORS pour le frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5500")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Création du dossier uploads s'il n'existe pas
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Servir les fichiers statiques (images uploadées)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# Endpoint de login owner (mot de passe)
@app.post("/login")
def login_owner(password: str = Form(...)):
    return owner_login(password)


# ==================== API KEY MANAGEMENT ====================

@app.post("/api-keys", response_model=APIKeyWithSecret, status_code=201, dependencies=[Depends(verify_owner)])
def create_api_key(
    key_create: APIKeyCreate,
    db: Session = Depends(get_db)
):
    """Génère une nouvelle clé API"""
    # Générer une clé aléatoire
    raw_key = secrets.token_urlsafe(48)
    hashed_key = hash_api_key(raw_key)

    # Créer l'entrée en base de données
    db_key = models.APIKey(
        key=hashed_key,
        name=key_create.name,
        is_active=True
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    # Retourner la clé (une seule fois)
    return {
        "id": db_key.id,
        "key": raw_key,
        "name": db_key.name,
        "is_active": db_key.is_active,
        "created_at": db_key.created_at,
        "last_used_at": db_key.last_used_at
    }


@app.get("/api-keys", response_model=list[APIKeyResponse], dependencies=[Depends(verify_owner)])
def list_api_keys(db: Session = Depends(get_db)):
    """Liste toutes les clés API"""
    keys = db.query(models.APIKey).all()
    return keys


@app.delete("/api-keys/{key_id}", status_code=204, dependencies=[Depends(verify_owner)])
def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """Supprime une clé API"""
    db_key = db.query(models.APIKey).filter(models.APIKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="Clé API non trouvée.")
    db.delete(db_key)
    db.commit()


# Inclusion des routes
app.include_router(trades.router, prefix="/trades", tags=["Trades"])
app.include_router(stats.router, prefix="/stats", tags=["Statistics"])
app.include_router(uploads.router, prefix="/trades", tags=["Uploads"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": "Trading Journal API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de vérification de santé pour Render"""
    return {"status": "ok"}
