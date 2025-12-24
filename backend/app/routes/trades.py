"""
Routes CRUD pour les trades
POST /trades - Créer un trade
GET /trades - Lister les trades avec filtres
GET /trades/{id} - Détail d'un trade
PUT /trades/{id} - Mettre à jour un trade
DELETE /trades/{id} - Supprimer un trade
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import verify_owner
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import (
    TradeCreate, TradeResponse, TradeUpdate, 
    TradeListResponse, SessionType
)

router = APIRouter()


@router.post("", response_model=TradeResponse, status_code=201, dependencies=[Depends(verify_owner)])
def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    """
    Crée un nouveau trade.
    
    Exemple de body:
    ```json
    {
        "date": "2024-12-20T10:30:00",
        "instrument": "XAUUSD",
        "session": "London",
        "setup": "CRT",
        "direction": "Buy",
        "timeframe": "M15",
        "entry": 2650.50,
        "stop_loss": 2645.00,
        "take_profit": 2665.00,
        "risk_pct": 1.0,
        "risk_usd": 100,
        "rr_expected": 2.5,
        "result_r": 2.0,
        "pnl_usd": 200,
        "duration_min": 45,
        "respected_plan": true,
        "mental_state": 4,
        "notes": "Belle entrée sur CRT confirmé"
    }
    ```
    """
    return crud.create_trade(db=db, trade=trade)


@router.get("", response_model=TradeListResponse)
def get_trades(
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Nombre de trades par page"),
    instrument: Optional[str] = Query(None, description="Filtrer par instrument"),
    session: Optional[str] = Query(None, description="Filtrer par session"),
    setup: Optional[str] = Query(None, description="Filtrer par setup"),
    direction: Optional[str] = Query(None, description="Filtrer par direction (Buy/Sell)"),
    date_from: Optional[datetime] = Query(None, description="Date de début"),
    date_to: Optional[datetime] = Query(None, description="Date de fin"),
    is_winner: Optional[bool] = Query(None, description="Filtrer gagnants/perdants"),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des trades avec pagination et filtres.
    
    Paramètres de filtre:
    - instrument: XAUUSD, EURUSD, etc.
    - session: Asia, London, NY, Overlap
    - setup: CRT, BOS, AMEDR, etc.
    - direction: Buy ou Sell
    - date_from / date_to: plage de dates
    - is_winner: true pour les trades gagnants, false pour perdants
    """
    skip = (page - 1) * page_size
    
    trades = crud.get_trades(
        db=db,
        skip=skip,
        limit=page_size,
        instrument=instrument,
        session=session,
        setup=setup,
        direction=direction,
        date_from=date_from,
        date_to=date_to,
        is_winner=is_winner
    )
    
    total = crud.count_trades(
        db=db,
        instrument=instrument,
        session=session,
        setup=setup,
        date_from=date_from,
        date_to=date_to
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return TradeListResponse(
        trades=trades,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/filters", response_model=dict)
def get_filter_options(db: Session = Depends(get_db)):
    """
    Récupère les options de filtrage disponibles.
    Retourne les listes uniques d'instruments et setups.
    """
    return {
        "instruments": crud.get_unique_instruments(db),
        "setups": crud.get_unique_setups(db),
        "sessions": [s.value for s in SessionType],
        "directions": ["Buy", "Sell"]
    }


@router.get("/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: int, db: Session = Depends(get_db)):
    """
    Récupère le détail d'un trade par son ID.
    Inclut les images associées.
    """
    trade = crud.get_trade(db=db, trade_id=trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade non trouvé")
    return trade


@router.put("/{trade_id}", response_model=TradeResponse, dependencies=[Depends(verify_owner)])
def update_trade(trade_id: int, trade: TradeUpdate, db: Session = Depends(get_db)):
    """
    Met à jour un trade existant.
    Seuls les champs fournis seront mis à jour.
    """
    updated_trade = crud.update_trade(db=db, trade_id=trade_id, trade_update=trade)
    if not updated_trade:
        raise HTTPException(status_code=404, detail="Trade non trouvé")
    return updated_trade


@router.delete("/{trade_id}", status_code=204, dependencies=[Depends(verify_owner)])
def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    """
    Supprime un trade et toutes ses images associées.
    """
    if not crud.delete_trade(db=db, trade_id=trade_id):
        raise HTTPException(status_code=404, detail="Trade non trouvé")
    return None
