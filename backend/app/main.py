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


from app.database import engine, Base
from app.routes import trades, stats, uploads
from fastapi import Response, Request, Depends, Form
from app.dependencies import owner_login, verify_owner

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
