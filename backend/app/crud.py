"""
Opérations CRUD pour les trades et images
Couche d'accès aux données
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models import Trade, TradeImage, SessionType, ErrorType, ImageType
from app.schemas import TradeCreate, TradeUpdate, TradeImageCreate


# ==================== TRADES ====================

def create_trade(db: Session, trade: TradeCreate) -> Trade:
    """Crée un nouveau trade"""
    db_trade = Trade(**trade.model_dump())
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade


def get_trade(db: Session, trade_id: int) -> Optional[Trade]:
    """Récupère un trade par son ID"""
    return db.query(Trade).filter(Trade.id == trade_id).first()


def get_trades(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    instrument: Optional[str] = None,
    session: Optional[str] = None,
    setup: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    direction: Optional[str] = None,
    is_winner: Optional[bool] = None
) -> List[Trade]:
    """
    Récupère une liste de trades avec filtres optionnels.
    """
    query = db.query(Trade)
    
    # Application des filtres
    if instrument:
        query = query.filter(Trade.instrument == instrument)
    if session:
        query = query.filter(Trade.session == session)
    if setup:
        query = query.filter(Trade.setup == setup)
    if direction:
        query = query.filter(Trade.direction == direction)
    if date_from:
        query = query.filter(Trade.date >= date_from)
    if date_to:
        query = query.filter(Trade.date <= date_to)
    if is_winner is not None:
        if is_winner:
            query = query.filter(Trade.result_r > 0)
        else:
            query = query.filter(Trade.result_r <= 0)
    
    return query.order_by(desc(Trade.date)).offset(skip).limit(limit).all()


def count_trades(
    db: Session,
    instrument: Optional[str] = None,
    session: Optional[str] = None,
    setup: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> int:
    """Compte le nombre total de trades avec filtres"""
    query = db.query(func.count(Trade.id))
    
    if instrument:
        query = query.filter(Trade.instrument == instrument)
    if session:
        query = query.filter(Trade.session == session)
    if setup:
        query = query.filter(Trade.setup == setup)
    if date_from:
        query = query.filter(Trade.date >= date_from)
    if date_to:
        query = query.filter(Trade.date <= date_to)
    
    return query.scalar()


def update_trade(db: Session, trade_id: int, trade_update: TradeUpdate) -> Optional[Trade]:
    """Met à jour un trade existant"""
    db_trade = get_trade(db, trade_id)
    if not db_trade:
        return None
    
    update_data = trade_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_trade, field, value)
    
    db_trade.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_trade)
    return db_trade


def delete_trade(db: Session, trade_id: int) -> bool:
    """Supprime un trade et ses images associées"""
    db_trade = get_trade(db, trade_id)
    if not db_trade:
        return False
    
    db.delete(db_trade)
    db.commit()
    return True


def get_all_trades(db: Session) -> List[Trade]:
    """Récupère tous les trades (pour les statistiques)"""
    return db.query(Trade).order_by(Trade.date).all()


def get_unique_setups(db: Session) -> List[str]:
    """Récupère la liste des setups uniques"""
    result = db.query(Trade.setup).distinct().all()
    return [r[0] for r in result]


def get_unique_instruments(db: Session) -> List[str]:
    """Récupère la liste des instruments uniques"""
    result = db.query(Trade.instrument).distinct().all()
    return [r[0] for r in result]


# ==================== TRADE IMAGES ====================

def create_trade_image(
    db: Session,
    trade_id: int,
    image_url: str,
    image_type: ImageType = ImageType.ANALYSIS,
    caption: Optional[str] = None
) -> Optional[TradeImage]:
    """Ajoute une image à un trade"""
    # Vérifier que le trade existe
    trade = get_trade(db, trade_id)
    if not trade:
        return None
    
    db_image = TradeImage(
        trade_id=trade_id,
        image_url=image_url,
        image_type=image_type,
        caption=caption
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_trade_images(db: Session, trade_id: int) -> List[TradeImage]:
    """Récupère toutes les images d'un trade"""
    return db.query(TradeImage).filter(TradeImage.trade_id == trade_id).all()


def delete_trade_image(db: Session, image_id: int) -> bool:
    """Supprime une image"""
    db_image = db.query(TradeImage).filter(TradeImage.id == image_id).first()
    if not db_image:
        return False
    
    db.delete(db_image)
    db.commit()
    return True


def get_image(db: Session, image_id: int) -> Optional[TradeImage]:
    """Récupère une image par son ID"""
    return db.query(TradeImage).filter(TradeImage.id == image_id).first()
