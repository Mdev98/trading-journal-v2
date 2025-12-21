"""
Modèles SQLAlchemy pour le journal de trading
Trade: Enregistrement d'un trade
TradeImage: Images associées à un trade
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class SessionType(str, enum.Enum):
    """Sessions de trading"""
    ASIA = "Asia"
    LONDON = "London"
    NY = "NY"
    OVERLAP = "Overlap"


class ErrorType(str, enum.Enum):
    """Types d'erreurs de trading"""
    NONE = "None"
    FOMO = "FOMO"
    REVENGE = "Revenge"
    OVERSIZE = "Oversize"
    NO_SL = "No SL"
    EARLY_EXIT = "Early Exit"
    LATE_ENTRY = "Late Entry"
    WRONG_SETUP = "Wrong Setup"
    NEWS_IGNORED = "News Ignored"
    OVERTRADING = "Overtrading"
    OTHER = "Other"


class ImageType(str, enum.Enum):
    """Types d'images de trade"""
    BEFORE = "before"
    DURING = "during"
    AFTER = "after"
    ANALYSIS = "analysis"


class Trade(Base):
    """
    Modèle principal d'un trade.
    Contient toutes les informations nécessaires au suivi et aux statistiques.
    """
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    date = Column(DateTime, nullable=False, index=True)
    instrument = Column(String(20), nullable=False, index=True)  # XAUUSD, EURUSD...
    session = Column(Enum(SessionType), nullable=False, index=True)
    setup = Column(String(50), nullable=False, index=True)  # CRT, BOS, AMEDR...
    direction = Column(String(10), nullable=False)  # Buy / Sell
    timeframe = Column(String(10), nullable=False)  # M1, M5, M15, H1...
    
    # Prix et niveaux
    entry = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=True)
    
    # Gestion du risque
    risk_pct = Column(Float, nullable=False)  # % du capital risqué
    risk_usd = Column(Float, nullable=False)  # Montant en USD risqué
    rr_expected = Column(Float, nullable=False)  # Risk/Reward attendu
    
    # Résultats
    result_r = Column(Float, nullable=True)  # Résultat en R (multiples du risque)
    pnl_usd = Column(Float, nullable=True)  # P&L en USD
    duration_min = Column(Integer, nullable=True)  # Durée en minutes
    
    # Discipline et psychologie
    respected_plan = Column(Boolean, default=True)
    error = Column(Boolean, default=False)
    error_type = Column(Enum(ErrorType), default=ErrorType.NONE)
    mental_state = Column(Integer, nullable=True)  # 1 à 5
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    images = relationship("TradeImage", back_populates="trade", cascade="all, delete-orphan")

    @property
    def is_winner(self) -> bool:
        """Retourne True si le trade est gagnant"""
        return self.result_r is not None and self.result_r > 0
    
    @property
    def is_loser(self) -> bool:
        """Retourne True si le trade est perdant"""
        return self.result_r is not None and self.result_r < 0
    
    @property
    def is_breakeven(self) -> bool:
        """Retourne True si le trade est à breakeven"""
        return self.result_r is not None and self.result_r == 0


class TradeImage(Base):
    """
    Images associées à un trade.
    Permet de stocker les screenshots TradingView avant/pendant/après.
    """
    __tablename__ = "trade_images"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(500), nullable=False)
    image_type = Column(Enum(ImageType), default=ImageType.ANALYSIS)
    caption = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    trade = relationship("Trade", back_populates="images")
