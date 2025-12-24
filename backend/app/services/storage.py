"""
Service de stockage d'images sur Supabase Storage
Gère l'upload, la récupération et la suppression des images
"""
import os
import uuid
from typing import Optional
from supabase import create_client, Client

# Configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Service Role Key pour le storage
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "trade-images")

# Client Supabase (singleton)
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Retourne le client Supabase (singleton).
    Retourne None si les credentials ne sont pas configurés.
    """
    global _supabase_client
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    return _supabase_client


def is_supabase_configured() -> bool:
    """Vérifie si Supabase Storage est configuré. Retourne False en local (dev)."""
    # Si on est en dev/local, on force le stockage local
    env = os.getenv("ENV", "dev").lower()
    if env in ["dev", "local", "development"]:
        return False
    return bool(SUPABASE_URL and SUPABASE_KEY)


def upload_to_supabase(file_content: bytes, filename: str, trade_id: int, content_type: str) -> Optional[str]:
    """
    Upload un fichier vers Supabase Storage.
    
    Args:
        file_content: Contenu du fichier en bytes
        filename: Nom original du fichier
        trade_id: ID du trade associé
        content_type: Type MIME du fichier
        
    Returns:
        URL publique du fichier ou None en cas d'erreur
    """
    client = get_supabase_client()
    if not client:
        return None
    
    try:
        # Générer un chemin unique
        ext = os.path.splitext(filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = f"trades/{trade_id}/{unique_filename}"
        
        # Upload vers Supabase Storage
        result = client.storage.from_(SUPABASE_BUCKET).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": content_type}
        )
        
        # Récupérer l'URL publique
        public_url = client.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
        
        return public_url
        
    except Exception as e:
        print(f"Erreur upload Supabase: {e}")
        return None


def delete_from_supabase(image_url: str) -> bool:
    """
    Supprime un fichier de Supabase Storage.
    
    Args:
        image_url: URL publique du fichier
        
    Returns:
        True si suppression réussie, False sinon
    """
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # Extraire le chemin depuis l'URL
        # URL format: https://xxx.supabase.co/storage/v1/object/public/bucket/path
        if SUPABASE_BUCKET in image_url:
            path = image_url.split(f"{SUPABASE_BUCKET}/")[1]
            client.storage.from_(SUPABASE_BUCKET).remove([path])
            return True
    except Exception as e:
        print(f"Erreur suppression Supabase: {e}")
    
    return False


def ensure_bucket_exists():
    """
    S'assure que le bucket existe, le crée si nécessaire.
    À appeler au démarrage de l'application.
    """
    client = get_supabase_client()
    if not client:
        return
    
    try:
        # Lister les buckets existants
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if SUPABASE_BUCKET not in bucket_names:
            # Créer le bucket en mode public
            client.storage.create_bucket(
                SUPABASE_BUCKET,
                options={"public": True}
            )
            print(f"Bucket '{SUPABASE_BUCKET}' créé avec succès")
    except Exception as e:
        print(f"Erreur création bucket: {e}")
