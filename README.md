# Trading Journal

Application privée de journal de trading pour prop firm trader.

## 🏗️ Architecture

```
trading_journal/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── main.py         # Point d'entrée
│   │   ├── database.py     # Config DB
│   │   ├── models.py       # Modèles SQLAlchemy
│   │   ├── schemas.py      # Schémas Pydantic
│   │   ├── crud.py         # Opérations CRUD
│   │   ├── routes/         # Endpoints API
│   │   └── services/       # Logique métier
│   └── requirements.txt
└── frontend/          # Interface utilisateur
    ├── index.html
    ├── css/
    └── js/
```

## 🚀 Démarrage rapide

### Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source .venv/bin/activate  # macOS/Linux
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Copier et configurer l'environnement
cp .env.example .env

# Lancer le serveur
uvicorn app.main:app --reload --port 8000
```

L'API sera disponible sur http://localhost:8000

Documentation Swagger: http://localhost:8000/docs

### Frontend

Ouvrir `frontend/index.html` dans un navigateur, ou utiliser un serveur local:

```bash
cd frontend
python -m http.server 5500
# ou avec Live Server dans VS Code
```

## 🔐 Authentification

L'API supporte deux méthodes d'authentification:

### 1. JWT Token (Frontend)
```bash
# Login avec mot de passe
TOKEN=$(curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "password=YOUR_PASSWORD" | jq -r '.access_token')

# Utiliser le token
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/trades
```

### 2. API Key (Scripts/Automations)
```bash
# Générer une clé API (depuis le frontend ou avec JWT token)
curl -X POST http://localhost:8000/api-keys \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Mon script Python"}'

# Utiliser la clé API
curl -H "X-API-Key: your_api_key_here" http://localhost:8000/trades
```

**Endpoints API Key Management:**
- `POST /api-keys` 🔒 — Créer une clé API
- `GET /api-keys` 🔒 — Lister les clés API
- `DELETE /api-keys/{id}` 🔒 — Révoquer une clé API

---

## 📊 Endpoints API

> Les endpoints marqués 🔒 nécessitent l'authentification via `Authorization: Bearer <token>` OU `X-API-Key: <key>`.

---

### Trades

#### `POST /trades` 🔒 — Créer un trade

**Body JSON :**
| Champ | Type | Requis | Description |
|---|---|---|---|
| `date` | datetime | ✅ | Date/heure du trade (ISO 8601) |
| `instrument` | string | ✅ | Ex: `XAUUSD`, `EURUSD` (max 20 car.) |
| `session` | string | ✅ | `Asia` \| `London` \| `NY` \| `Overlap` |
| `setup` | string | ✅ | Ex: `CRT`, `BOS`, `AMEDR` (max 50 car.) |
| `direction` | string | ✅ | `Buy` \| `Sell` |
| `timeframe` | string | ✅ | Ex: `M15`, `H1` |
| `entry` | float | ✅ | Prix d'entrée (> 0) |
| `stop_loss` | float | ✅ | Prix du stop loss (> 0) |
| `take_profit` | float | ➖ | Prix du take profit (> 0) |
| `risk_pct` | float | ✅ | Risque en % du capital (0–100) |
| `risk_usd` | float | ✅ | Risque en USD (> 0) |
| `rr_expected` | float | ✅ | RR attendu (> 0) |
| `result_r` | float | ➖ | Résultat en R (négatif si perte) |
| `pnl_usd` | float | ➖ | P&L en USD |
| `duration_min` | int | ➖ | Durée du trade en minutes (≥ 0) |
| `respected_plan` | bool | ➖ | A-t-on respecté le plan ? (défaut: `true`) |
| `error` | bool | ➖ | Y a-t-il eu une erreur ? (défaut: `false`) |
| `error_type` | string | ➖ | `None` \| `FOMO` \| `Revenge` \| `Oversize` \| `No SL` \| `Early Exit` \| `Late Entry` \| `Wrong Setup` \| `News Ignored` \| `Overtrading` \| `Other` |
| `mental_state` | int | ➖ | État mental de 1 (mauvais) à 5 (excellent) |
| `notes` | string | ➖ | Notes libres |

**Réponse `201` — `TradeResponse` :**
```json
{
  "id": 42,
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
  "error": false,
  "error_type": "None",
  "mental_state": 4,
  "notes": "Belle entrée sur CRT confirmé",
  "is_winner": true,
  "is_loser": false,
  "is_breakeven": false,
  "images": [],
  "created_at": "2024-12-20T10:45:00",
  "updated_at": "2024-12-20T10:45:00"
}
```

---

#### `GET /trades` — Lister les trades

**Query params :**
| Param | Type | Défaut | Description |
|---|---|---|---|
| `page` | int | `1` | Numéro de page (≥ 1) |
| `page_size` | int | `20` | Trades par page (1–100) |
| `instrument` | string | — | Filtrer par instrument |
| `session` | string | — | Filtrer par session |
| `setup` | string | — | Filtrer par setup |
| `direction` | string | — | `Buy` \| `Sell` |
| `date_from` | datetime | — | Date de début (ISO 8601) |
| `date_to` | datetime | — | Date de fin (ISO 8601) |
| `is_winner` | bool | — | `true` = gagnants, `false` = perdants |

**Réponse `200` — `TradeListResponse` :**
```json
{
  "trades": [ /* liste de TradeResponse */ ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

---

#### `GET /trades/filters` — Options de filtrage

**Paramètres :** aucun

**Réponse `200` :**
```json
{
  "instruments": ["XAUUSD", "EURUSD"],
  "setups": ["CRT", "BOS", "AMEDR"],
  "sessions": ["Asia", "London", "NY", "Overlap"],
  "directions": ["Buy", "Sell"]
}
```

---

#### `GET /trades/{id}` — Détail d'un trade

**Path param :** `id` (int) — identifiant du trade

**Réponse `200` :** `TradeResponse` (avec images incluses)
**Erreur `404` :** trade non trouvé

---

#### `PUT /trades/{id}` 🔒 — Modifier un trade

**Path param :** `id` (int)

**Body JSON :** tous les champs sont optionnels (mise à jour partielle), mêmes champs que `POST /trades`.

**Réponse `200` :** `TradeResponse` mis à jour
**Erreur `404` :** trade non trouvé

---

#### `DELETE /trades/{id}` 🔒 — Supprimer un trade

**Path param :** `id` (int)

Supprime le trade **et toutes ses images** associées.

**Réponse `204` :** aucun contenu
**Erreur `404` :** trade non trouvé

---

### Images

#### `POST /trades/{id}/images` 🔒 — Upload d'images

**Path param :** `id` (int) — identifiant du trade

**Body `multipart/form-data` :**
| Champ | Type | Requis | Description |
|---|---|---|---|
| `files` | fichiers | ✅ | 1 à 10 images (JPG, PNG, GIF, WebP, max 10 MB/fichier) |
| `image_type` | string | ➖ | `before` \| `during` \| `after` \| `analysis` (défaut: `analysis`) |
| `caption` | string | ➖ | Légende optionnelle |

**Réponse `201` — liste de `TradeImageResponse` :**
```json
[
  {
    "id": 7,
    "trade_id": 42,
    "image_url": "https://...supabase.../trade-42-uuid.png",
    "image_type": "analysis",
    "caption": "Setup H1",
    "created_at": "2024-12-20T10:50:00"
  }
]
```
**Erreur `404` :** trade non trouvé
**Erreur `400` :** extension non autorisée ou plus de 10 fichiers

---

#### `GET /trades/{id}/images` — Liste des images d'un trade

**Path param :** `id` (int)

**Réponse `200` :** liste de `TradeImageResponse`
**Erreur `404` :** trade non trouvé

---

#### `DELETE /trades/images/{id}` 🔒 — Supprimer une image

**Path param :** `id` (int) — identifiant de l'image

Supprime l'entrée en base **et le fichier** (Supabase ou local).

**Réponse `204` :** aucun contenu
**Erreur `404` :** image non trouvée

---

#### `GET /trades/storage/status` — Statut du stockage

**Paramètres :** aucun

**Réponse `200` :**
```json
{
  "storage_type": "supabase",
  "supabase_configured": true
}
```

---

### Statistiques

> Tous les endpoints de stats acceptent les **query params communs** suivants :
>
> | Param | Type | Description |
> |---|---|---|
> | `date_from` | datetime | Date de début (ISO 8601) |
> | `date_to` | datetime | Date de fin (ISO 8601) |
> | `instrument` | string | Filtrer par instrument |
> | `setup` | string | Filtrer par setup |

---

#### `GET /stats/global` — Statistiques globales

**Réponse `200` — `GlobalStats` :**
```json
{
  "total_trades": 120,
  "winning_trades": 72,
  "losing_trades": 42,
  "breakeven_trades": 6,
  "winrate": 60.0,
  "avg_win_r": 1.8,
  "avg_loss_r": -1.0,
  "expectancy": 0.68,
  "profit_factor": 2.1,
  "total_pnl_usd": 3200.0,
  "total_r": 81.6,
  "max_drawdown_r": -4.5,
  "max_drawdown_pct": -5.2,
  "avg_rr_expected": 2.3,
  "avg_rr_actual": 1.8,
  "discipline_rate": 88.3,
  "avg_duration_min": 52.0
}
```

---

#### `GET /stats/by-setup` — Stats par setup

**Réponse `200` — liste de `SetupStats` (triée par `total_r` décroissant) :**
```json
[
  {
    "setup": "CRT",
    "total_trades": 55,
    "winrate": 65.0,
    "expectancy": 0.82,
    "total_r": 45.1,
    "avg_rr": 2.1,
    "profit_factor": 2.5
  }
]
```

---

#### `GET /stats/by-session` — Stats par session

**Réponse `200` — liste de `SessionStats` :**
```json
[
  {
    "session": "London",
    "total_trades": 60,
    "winrate": 63.0,
    "expectancy": 0.75,
    "total_r": 45.0,
    "avg_rr": 2.0
  }
]
```

---

#### `GET /stats/daily` — Stats journalières

**Query param supplémentaire :**
| Param | Type | Défaut | Description |
|---|---|---|---|
| `days` | int | `30` | Nombre de jours à inclure (1–365) |

**Réponse `200` — liste de `DailyStats` :**
```json
[
  {
    "date": "2024-12-20",
    "total_trades": 3,
    "winning_trades": 2,
    "losing_trades": 1,
    "total_r": 2.5,
    "pnl_usd": 250.0,
    "winrate": 66.7
  }
]
```

---

#### `GET /stats/weekly` — Stats hebdomadaires

**Query param supplémentaire :**
| Param | Type | Défaut | Description |
|---|---|---|---|
| `weeks` | int | `12` | Nombre de semaines à inclure (1–52) |

**Réponse `200` — liste de `WeeklyStats` :**
```json
[
  {
    "week_start": "2024-12-16",
    "week_end": "2024-12-22",
    "total_trades": 12,
    "winning_trades": 8,
    "losing_trades": 4,
    "total_r": 9.2,
    "pnl_usd": 920.0,
    "winrate": 66.7,
    "expectancy": 0.77
  }
]
```

---

#### `GET /stats/errors` — Analyse des erreurs

**Réponse `200` — liste de `ErrorStats` :**
```json
[
  {
    "error_type": "FOMO",
    "count": 8,
    "percentage": 30.0,
    "avg_loss_r": -1.4
  }
]
```

---

#### `GET /stats/mental` — Corrélation état mental / résultats

**Réponse `200` — liste de `MentalStateStats` (un objet par niveau 1–5) :**
```json
[
  {
    "mental_state": 5,
    "total_trades": 30,
    "winrate": 73.0,
    "avg_result_r": 1.1
  }
]
```

---

#### `GET /stats/equity-curve` — Courbe d'equity

**Réponse `200` — liste de `EquityPoint` (un point par trade, ordre chronologique) :**
```json
[
  {
    "date": "2024-12-20",
    "cumulative_r": 81.6,
    "cumulative_pnl": 3200.0,
    "trade_count": 120
  }
]
```

## 🌐 Déploiement

### Backend sur Render

1. Créer un nouveau Web Service sur Render
2. Connecter le repo GitHub
3. Configurer:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Ajouter les variables d'environnement:
   - `DATABASE_URL` (PostgreSQL)
   - `FRONTEND_URL` (URL Netlify)

### Frontend sur Netlify

1. Créer un nouveau site sur Netlify
2. Connecter le repo GitHub
3. Configurer:
   - **Publish directory**: `frontend`
4. Modifier `frontend/js/config.js` avec l'URL du backend Render

## 📈 Statistiques calculées

- **Winrate**: % de trades gagnants
- **Expectancy**: Espérance de gain en R
- **Profit Factor**: Gains bruts / Pertes brutes
- **Max Drawdown**: Perte maximale depuis un pic
- **Discipline Rate**: % de trades respectant le plan
- **Corrélation mentale**: Impact de l'état mental sur les résultats

## 🛠️ Exemples d'utilisation

### Python avec clé API
```python
import requests
from datetime import datetime

API_KEY = "your_api_key_here"
BASE_URL = "http://localhost:8000"

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Créer un trade
trade = requests.post(f"{BASE_URL}/trades", headers=headers, json={
    "date": datetime.now().isoformat(),
    "instrument": "XAUUSD",
    "session": "London",
    "setup": "CRT",
    "direction": "Buy",
    "timeframe": "M15",
    "entry": 2650.50,
    "stop_loss": 2645.00,
    "risk_pct": 1.0,
    "risk_usd": 100,
    "rr_expected": 2.5
}).json()

print(f"Trade créé: ID={trade['id']}")

# Récupérer les stats
stats = requests.get(f"{BASE_URL}/stats/global", headers=headers).json()
print(f"Winrate: {stats['winrate']:.1f}%")
```

### cURL avec clé API
```bash
API_KEY="your_api_key_here"

# Créer un trade
curl -X POST http://localhost:8000/trades \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-12-20T10:30:00",
    "instrument": "XAUUSD",
    "session": "London",
    "setup": "CRT",
    "direction": "Buy",
    "timeframe": "M15",
    "entry": 2650.50,
    "stop_loss": 2645.00,
    "risk_pct": 1.0,
    "risk_usd": 100,
    "rr_expected": 2.5
  }'
```

## 📚 Client Python réutilisable
Un client Python prêt à l'emploi est disponible dans `backend/trade_client.py` pour faciliter l'intégration.
