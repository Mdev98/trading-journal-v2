#!/usr/bin/env python3
"""
Client Python pour ajouter des trades avec clé API
Utilisation:
    python trade_client.py
"""
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"  # Changer pour production
API_KEY = "your_api_key_here"  # Remplacer par votre clé API

class TradeClient:
    def __init__(self, api_key, base_url=API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def create_trade(self, trade_data):
        """Crée un nouveau trade"""
        response = requests.post(
            f"{self.base_url}/trades",
            json=trade_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_trades(self, page=1, page_size=20, filters=None):
        """Récupère la liste des trades avec optionnellement des filtres"""
        params = {"page": page, "page_size": page_size}
        if filters:
            params.update(filters)
        response = requests.get(
            f"{self.base_url}/trades",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_trade(self, trade_id):
        """Récupère les détails d'un trade"""
        response = requests.get(
            f"{self.base_url}/trades/{trade_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def update_trade(self, trade_id, trade_data):
        """Met à jour un trade"""
        response = requests.put(
            f"{self.base_url}/trades/{trade_id}",
            json=trade_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def delete_trade(self, trade_id):
        """Supprime un trade"""
        response = requests.delete(
            f"{self.base_url}/trades/{trade_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.status_code == 204

    def get_stats(self):
        """Récupère les statistiques globales"""
        response = requests.get(
            f"{self.base_url}/stats/global",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le client
    client = TradeClient(API_KEY)

    try:
        # Créer un trade
        print("➕ Création d'un trade...")
        new_trade = client.create_trade({
            "date": datetime.now().isoformat(),
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
            "mental_state": 4,
            "notes": "Trade créé via API"
        })
        print(f"✓ Trade créé: ID={new_trade['id']}\n")

        # Récupérer les stats
        print("📊 Statistiques globales:")
        stats = client.get_stats()
        print(f"  Total trades: {stats['total_trades']}")
        print(f"  Winrate: {stats['winrate']:.1f}%")
        print(f"  Expectancy: {stats['expectancy']:.2f}R\n")

        # Récupérer les trades
        print("📋 Récentes trades:")
        trades = client.get_trades(page=1, page_size=5)
        for trade in trades['trades']:
            status = "✅" if trade.get('is_winner') else "❌" if trade.get('is_loser') else "⚪"
            print(f"  {status} {trade['instrument']} {trade['direction']} @ {trade['entry']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
