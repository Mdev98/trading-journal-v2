"""
Schémas Pydantic pour la validation et la sérialisation des données
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


# ==================== ENUMS ====================

class SessionType(str, Enum):
    ASIA = "Asia"
    LONDON = "London"
    NY = "NY"
    OVERLAP = "Overlap"


class ErrorType(str, Enum):
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


class ImageType(str, Enum):
    BEFORE = "before"
    DURING = "during"
    AFTER = "after"
    ANALYSIS = "analysis"


# ==================== TRADE IMAGE SCHEMAS ====================

class TradeImageBase(BaseModel):
    """Schéma de base pour une image de trade"""
    image_type: ImageType = ImageType.ANALYSIS
    caption: Optional[str] = None


class TradeImageCreate(TradeImageBase):
    """Schéma pour la création d'une image"""
    image_url: str


class TradeImageResponse(TradeImageBase):
    """Schéma de réponse pour une image"""
    id: int
    trade_id: int
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== TRADE SCHEMAS ====================

class TradeBase(BaseModel):
    """Schéma de base pour un trade"""
    date: datetime
    instrument: str = Field(..., min_length=1, max_length=20, example="XAUUSD")
    session: SessionType
    setup: str = Field(..., min_length=1, max_length=50, example="CRT")
    direction: str = Field(..., pattern="^(Buy|Sell)$")
    timeframe: str = Field(..., example="M15")
    
    entry: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: Optional[float] = Field(None, gt=0)
    
    risk_pct: float = Field(..., gt=0, le=100)
    risk_usd: float = Field(..., gt=0)
    rr_expected: float = Field(..., gt=0)
    
    result_r: Optional[float] = None
    pnl_usd: Optional[float] = None
    duration_min: Optional[int] = Field(None, ge=0)
    
    respected_plan: bool = True
    error: bool = False
    error_type: ErrorType = ErrorType.NONE
    mental_state: Optional[int] = Field(None, ge=1, le=5)
    
    notes: Optional[str] = None

    @validator('error_type', pre=True, always=True)
    def set_error_type(cls, v, values):
        """Si error est False, forcer error_type à NONE"""
        if values.get('error') is False:
            return ErrorType.NONE
        return v


class TradeCreate(TradeBase):
    """Schéma pour la création d'un trade"""
    pass


class TradeUpdate(BaseModel):
    """Schéma pour la mise à jour partielle d'un trade"""
    date: Optional[datetime] = None
    instrument: Optional[str] = None
    session: Optional[SessionType] = None
    setup: Optional[str] = None
    direction: Optional[str] = None
    timeframe: Optional[str] = None
    
    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    risk_pct: Optional[float] = None
    risk_usd: Optional[float] = None
    rr_expected: Optional[float] = None
    
    result_r: Optional[float] = None
    pnl_usd: Optional[float] = None
    duration_min: Optional[int] = None
    
    respected_plan: Optional[bool] = None
    error: Optional[bool] = None
    error_type: Optional[ErrorType] = None
    mental_state: Optional[int] = None
    
    notes: Optional[str] = None


class TradeResponse(TradeBase):
    """Schéma de réponse pour un trade"""
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[TradeImageResponse] = []
    
    # Champs calculés
    is_winner: bool = False
    is_loser: bool = False
    is_breakeven: bool = False

    class Config:
        from_attributes = True

    @validator('is_winner', pre=True, always=True)
    def calc_is_winner(cls, v, values):
        result_r = values.get('result_r')
        return result_r is not None and result_r > 0

    @validator('is_loser', pre=True, always=True)
    def calc_is_loser(cls, v, values):
        result_r = values.get('result_r')
        return result_r is not None and result_r < 0

    @validator('is_breakeven', pre=True, always=True)
    def calc_is_breakeven(cls, v, values):
        result_r = values.get('result_r')
        return result_r is not None and result_r == 0


class TradeListResponse(BaseModel):
    """Schéma de réponse pour une liste de trades avec pagination"""
    trades: List[TradeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== STATISTICS SCHEMAS ====================

class GlobalStats(BaseModel):
    """Statistiques globales"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int
    winrate: float  # en %
    avg_win_r: float
    avg_loss_r: float
    expectancy: float  # en R
    profit_factor: float
    total_pnl_usd: float
    total_r: float
    max_drawdown_r: float
    max_drawdown_pct: float
    avg_rr_expected: float
    avg_rr_actual: float
    discipline_rate: float  # % trades respectant le plan
    avg_duration_min: float


class SetupStats(BaseModel):
    """Statistiques par setup"""
    setup: str
    total_trades: int
    winrate: float
    expectancy: float
    total_r: float
    avg_rr: float
    profit_factor: float


class SessionStats(BaseModel):
    """Statistiques par session"""
    session: str
    total_trades: int
    winrate: float
    expectancy: float
    total_r: float
    avg_rr: float


class DailyStats(BaseModel):
    """Statistiques journalières"""
    date: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_r: float
    pnl_usd: float
    winrate: float


class WeeklyStats(BaseModel):
    """Statistiques hebdomadaires"""
    week_start: str
    week_end: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_r: float
    pnl_usd: float
    winrate: float
    expectancy: float


class ErrorStats(BaseModel):
    """Statistiques des erreurs"""
    error_type: str
    count: int
    percentage: float
    avg_loss_r: float


class MentalStateStats(BaseModel):
    """Corrélation état mental / résultat"""
    mental_state: int
    total_trades: int
    winrate: float
    avg_result_r: float


class EquityPoint(BaseModel):
    """Point sur la courbe d'equity"""
    date: str
    cumulative_r: float
    cumulative_pnl: float
    trade_count: int
