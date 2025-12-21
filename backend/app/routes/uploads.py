"""
Routes pour l'upload et la gestion des images
POST /trades/{id}/images - Upload d'images pour un trade
GET /trades/{id}/images - Liste des images d'un trade
DELETE /images/{id} - Suppression d'une image
"""
import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import TradeImageResponse, ImageType
from app.models import ImageType as ImageTypeEnum

router = APIRouter()

# Configuration du dossier d'upload
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def validate_file(file: UploadFile) -> None:
    """Valide le fichier uploadé"""
    # Vérification de l'extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Extension non autorisée. Utilisez: {', '.join(ALLOWED_EXTENSIONS)}"
        )


def save_upload_file(file: UploadFile, trade_id: int) -> str:
    """
    Sauvegarde le fichier uploadé et retourne l'URL.
    Organise les fichiers par trade_id.
    """
    # Créer le dossier pour ce trade
    trade_dir = os.path.join(UPLOAD_DIR, str(trade_id))
    os.makedirs(trade_dir, exist_ok=True)
    
    # Générer un nom unique
    ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(trade_dir, unique_filename)
    
    # Sauvegarder le fichier
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Retourner l'URL relative
    return f"/uploads/{trade_id}/{unique_filename}"


@router.post("/{trade_id}/images", response_model=List[TradeImageResponse], status_code=201)
async def upload_images(
    trade_id: int,
    files: List[UploadFile] = File(..., description="Images à uploader (max 10)"),
    image_type: ImageType = Form(ImageType.ANALYSIS, description="Type d'image"),
    caption: str = Form(None, description="Légende optionnelle"),
    db: Session = Depends(get_db)
):
    """
    Upload une ou plusieurs images pour un trade.
    
    - Formats acceptés: JPG, PNG, GIF, WebP
    - Taille max: 10 MB par fichier
    - Max 10 fichiers par requête
    
    Types d'images:
    - before: Capture avant l'entrée
    - during: Pendant le trade
    - after: Après clôture
    - analysis: Analyse générale
    """
    # Vérifier que le trade existe
    trade = crud.get_trade(db, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade non trouvé")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 fichiers par upload")
    
    uploaded_images = []
    
    for file in files:
        # Valider le fichier
        validate_file(file)
        
        # Sauvegarder le fichier
        image_url = save_upload_file(file, trade_id)
        
        # Créer l'entrée en base
        db_image = crud.create_trade_image(
            db=db,
            trade_id=trade_id,
            image_url=image_url,
            image_type=ImageTypeEnum(image_type.value),
            caption=caption
        )
        
        if db_image:
            uploaded_images.append(db_image)
    
    return uploaded_images


@router.get("/{trade_id}/images", response_model=List[TradeImageResponse])
def get_trade_images(trade_id: int, db: Session = Depends(get_db)):
    """
    Récupère toutes les images d'un trade.
    """
    # Vérifier que le trade existe
    trade = crud.get_trade(db, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade non trouvé")
    
    return crud.get_trade_images(db, trade_id)


@router.delete("/images/{image_id}", status_code=204)
def delete_image(image_id: int, db: Session = Depends(get_db)):
    """
    Supprime une image spécifique.
    Supprime aussi le fichier physique.
    """
    # Récupérer l'image pour avoir le chemin
    image = crud.get_image(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image non trouvée")
    
    # Supprimer le fichier physique
    file_path = image.image_url.lstrip("/")
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Supprimer l'entrée en base
    crud.delete_trade_image(db, image_id)
    
    return None
