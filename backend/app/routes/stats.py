"""
Routes pour les statistiques de trading
GET /stats/global - Statistiques globales
GET /stats/by-setup - Stats par setup
GET /stats/by-session - Stats par session
GET /stats/daily - Stats journalières
GET /stats/weekly - Stats hebdomadaires
GET /stats/errors - Analyse des erreurs
GET /stats/mental - Corrélation état mental
GET /stats/equity-curve - Courbe d'equity
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import (
    GlobalStats, SetupStats, SessionStats,
    DailyStats, WeeklyStats, ErrorStats,
    MentalStateStats, EquityPoint
)
from app.services.statistics import StatisticsService

router = APIRouter()


def get_stats_service(
    db: Session = Depends(get_db),
    date_from: Optional[datetime] = Query(None, description="Date de début"),
    date_to: Optional[datetime] = Query(None, description="Date de fin"),
    instrument: Optional[str] = Query(None, description="Filtrer par instrument"),
    setup: Optional[str] = Query(None, description="Filtrer par setup")
) -> StatisticsService:
    """
    Dépendance pour créer le service de statistiques.
    Récupère les trades avec les filtres optionnels.
    """
    trades = crud.get_trades(
        db=db,
        skip=0,
        limit=10000,  # Récupérer tous les trades pour les stats
        date_from=date_from,
        date_to=date_to,
        instrument=instrument,
        setup=setup
    )
    return StatisticsService(trades)


@router.get("/global", response_model=GlobalStats)
def get_global_stats(service: StatisticsService = Depends(get_stats_service)):
    """
    Récupère les statistiques globales de trading.
    
    Inclut:
    - Winrate
    - Expectancy
    - Profit Factor
    - Drawdown max
    - P&L total
    - Discipline rate
    
    Filtres optionnels via query params:
    - date_from / date_to
    - instrument
    - setup
    """
    return service.calculate_global_stats()


@router.get("/by-setup", response_model=List[SetupStats])
def get_stats_by_setup(service: StatisticsService = Depends(get_stats_service)):
    """
    Récupère les statistiques par setup (CRT, BOS, AMEDR...).
    Trié par performance (total_r) décroissante.
    """
    return service.calculate_stats_by_setup()


@router.get("/by-session", response_model=List[SessionStats])
def get_stats_by_session(service: StatisticsService = Depends(get_stats_service)):
    """
    Récupère les statistiques par session de trading.
    Sessions: Asia, London, NY, Overlap
    """
    return service.calculate_stats_by_session()


@router.get("/daily", response_model=List[DailyStats])
def get_daily_stats(
    days: int = Query(30, ge=1, le=365, description="Nombre de jours"),
    service: StatisticsService = Depends(get_stats_service)
):
    """
    Récupère les statistiques journalières.
    Par défaut: 30 derniers jours.
    """
    return service.calculate_daily_stats(days=days)


@router.get("/weekly", response_model=List[WeeklyStats])
def get_weekly_stats(
    weeks: int = Query(12, ge=1, le=52, description="Nombre de semaines"),
    service: StatisticsService = Depends(get_stats_service)
):
    """
    Récupère les statistiques hebdomadaires.
    Par défaut: 12 dernières semaines.
    """
    return service.calculate_weekly_stats(weeks=weeks)


@router.get("/errors", response_model=List[ErrorStats])
def get_error_stats(service: StatisticsService = Depends(get_stats_service)):
    """
    Analyse les erreurs de trading les plus fréquentes.
    Inclut le type d'erreur, le nombre d'occurrences et la perte moyenne.
    """
    return service.calculate_error_stats()


@router.get("/mental", response_model=List[MentalStateStats])
def get_mental_stats(service: StatisticsService = Depends(get_stats_service)):
    """
    Analyse la corrélation entre l'état mental (1-5) et les résultats.
    Utile pour identifier l'impact de la psychologie sur la performance.
    """
    return service.calculate_mental_state_correlation()


@router.get("/equity-curve", response_model=List[EquityPoint])
def get_equity_curve(service: StatisticsService = Depends(get_stats_service)):
    """
    Génère les points de la courbe d'equity.
    Utile pour visualiser la progression du compte.
    """
    return service.calculate_equity_curve()
