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

## 📊 Endpoints API

> 🔐 Les endpoints marqués **[Auth]** nécessitent le header `X-Owner-Token`.
> 📄 Documentation interactive complète : http://localhost:8000/docs

---

### Trades

#### `POST /trades` [Auth]
Crée un nouveau trade.

**Body (JSON) :**
| Champ | Type | Requis | Description |
|---|---|---|---|
| `date` | datetime | ✅ | Date et heure du trade (ISO 8601) |
| `instrument` | string | ✅ | Ex : `XAUUSD`, `EURUSD` (1–20 caractères) |
| `session` | string | ✅ | `Asia`, `London`, `NY`, `Overlap` |
| `setup` | string | ✅ | Ex : `CRT`, `BOS` (1–50 caractères) |
| `direction` | string | ✅ | `Buy` ou `Sell` |
| `timeframe` | string | ✅ | Ex : `M15`, `H1` |
| `entry` | float | ✅ | Prix d'entrée (> 0) |
| `stop_loss` | float | ✅ | Prix du stop-loss (> 0) |
| `take_profit` | float | ❌ | Prix du take-profit (> 0) |
| `risk_pct` | float | ✅ | Risque en % du compte (0–100) |
| `risk_usd` | float | ✅ | Risque en USD (> 0) |
| `rr_expected` | float | ✅ | Ratio risque/rendement attendu (> 0) |
| `result_r` | float | ❌ | Résultat en R (positif = gain, négatif = perte) |
| `pnl_usd` | float | ❌ | P&L en USD |
| `duration_min` | int | ❌ | Durée du trade en minutes (≥ 0) |
| `respected_plan` | bool | ❌ | Respect du plan de trading (défaut : `true`) |
| `error` | bool | ❌ | Erreur commise (défaut : `false`) |
| `error_type` | string | ❌ | `None`, `FOMO`, `Revenge`, `Oversize`, `No SL`, `Early Exit`, `Late Entry`, `Wrong Setup`, `News Ignored`, `Overtrading`, `Other` |
| `mental_state` | int | ❌ | État mental de 1 (mauvais) à 5 (excellent) |
| `notes` | string | ❌ | Notes libres |

**Réponse `201` :** objet `Trade` complet (voir ci-dessous).

---

#### `GET /trades`
Récupère la liste des trades avec pagination et filtres optionnels.

**Query params :**
| Paramètre | Type | Défaut | Description |
|---|---|---|---|
| `page` | int | `1` | Numéro de page (≥ 1) |
| `page_size` | int | `20` | Trades par page (1–100) |
| `instrument` | string | — | Filtrer par instrument |
| `session` | string | — | Filtrer par session (`Asia`, `London`, `NY`, `Overlap`) |
| `setup` | string | — | Filtrer par setup |
| `direction` | string | — | `Buy` ou `Sell` |
| `date_from` | datetime | — | Date de début (ISO 8601) |
| `date_to` | datetime | — | Date de fin (ISO 8601) |
| `is_winner` | bool | — | `true` = trades gagnants, `false` = perdants |

**Réponse `200` :**
```json
{
  "trades": [ /* liste d'objets Trade */ ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

---

#### `GET /trades/filters`
Retourne les valeurs disponibles pour alimenter les menus de filtres.

**Aucun paramètre.**

**Réponse `200` :**
```json
{
  "instruments": ["XAUUSD", "EURUSD"],
  "setups": ["CRT", "BOS"],
  "sessions": ["Asia", "London", "NY", "Overlap"],
  "directions": ["Buy", "Sell"]
}
```

---

#### `GET /trades/{id}`
Récupère le détail d'un trade, images incluses.

**Path param :** `id` (int) — identifiant du trade.

**Réponse `200` :** objet `Trade` complet.
**Réponse `404` :** `{ "detail": "Trade non trouvé" }`

---

#### `PUT /trades/{id}` [Auth]
Met à jour partiellement un trade (seuls les champs fournis sont modifiés).

**Path param :** `id` (int).

**Body (JSON) :** tous les champs sont optionnels (mêmes champs que `POST /trades`).

**Réponse `200` :** objet `Trade` mis à jour.
**Réponse `404` :** `{ "detail": "Trade non trouvé" }`

---

#### `DELETE /trades/{id}` [Auth]
Supprime un trade et toutes ses images associées.

**Path param :** `id` (int).

**Réponse `204` :** aucun contenu.
**Réponse `404` :** `{ "detail": "Trade non trouvé" }`

---

#### Objet `Trade` (réponse)
```json
{
  "id": 1,
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
  "risk_usd": 100.0,
  "rr_expected": 2.5,
  "result_r": 2.0,
  "pnl_usd": 200.0,
  "duration_min": 45,
  "respected_plan": true,
  "error": false,
  "error_type": "None",
  "mental_state": 4,
  "notes": "Belle entrée sur CRT confirmé",
  "created_at": "2024-12-20T11:00:00",
  "updated_at": "2024-12-20T11:00:00",
  "images": [],
  "is_winner": true,
  "is_loser": false,
  "is_breakeven": false
}
```

---

### Images

#### `POST /trades/{id}/images` [Auth]
Upload une ou plusieurs images pour un trade. Envoi en `multipart/form-data`.

**Path param :** `id` (int) — identifiant du trade.

**Form data :**
| Champ | Type | Requis | Description |
|---|---|---|---|
| `files` | file[] | ✅ | Images à uploader (max 10 fichiers, max 10 MB chacun) |
| `image_type` | string | ❌ | `before`, `during`, `after`, `analysis` (défaut : `analysis`) |
| `caption` | string | ❌ | Légende optionnelle |

Formats acceptés : `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`.

**Réponse `201` :** liste d'objets `TradeImage`.
**Réponse `400` :** extension non autorisée ou plus de 10 fichiers.
**Réponse `404` :** trade introuvable.

---

#### `GET /trades/{id}/images`
Récupère toutes les images associées à un trade.

**Path param :** `id` (int).

**Réponse `200` :** liste d'objets `TradeImage`.
**Réponse `404` :** trade introuvable.

---

#### `DELETE /trades/images/{id}` [Auth]
Supprime une image (fichier et entrée en base).

**Path param :** `id` (int) — identifiant de l'image.

**Réponse `204` :** aucun contenu.
**Réponse `404` :** `{ "detail": "Image non trouvée" }`

---

#### `GET /trades/storage/status`
Indique si le stockage Supabase est actif ou si le stockage local est utilisé.

**Aucun paramètre.**

**Réponse `200` :**
```json
{
  "storage_type": "supabase",
  "supabase_configured": true
}
```

---

#### Objet `TradeImage` (réponse)
```json
{
  "id": 1,
  "trade_id": 42,
  "image_url": "https://…/trade-42-abc.jpg",
  "image_type": "before",
  "caption": "Setup avant entrée",
  "created_at": "2024-12-20T11:00:00"
}
```

---

### Statistiques

> Tous les endpoints de statistiques acceptent les **query params de filtre** suivants :
> | Paramètre | Type | Description |
> |---|---|---|
> | `date_from` | datetime | Date de début |
> | `date_to` | datetime | Date de fin |
> | `instrument` | string | Filtrer par instrument |
> | `setup` | string | Filtrer par setup |

---

#### `GET /stats/global`
Statistiques globales de trading.

**Réponse `200` :**
```json
{
  "total_trades": 120,
  "winning_trades": 72,
  "losing_trades": 42,
  "breakeven_trades": 6,
  "winrate": 60.0,
  "avg_win_r": 2.1,
  "avg_loss_r": -1.0,
  "expectancy": 0.86,
  "profit_factor": 3.0,
  "total_pnl_usd": 4200.0,
  "total_r": 58.5,
  "max_drawdown_r": -5.2,
  "max_drawdown_pct": 3.1,
  "avg_rr_expected": 2.5,
  "avg_rr_actual": 1.8,
  "discipline_rate": 88.3,
  "avg_duration_min": 42.0
}
```

---

#### `GET /stats/by-setup`
Statistiques agrégées par setup, triées par performance décroissante (`total_r`).

**Réponse `200` :** tableau d'objets :
```json
[
  {
    "setup": "CRT",
    "total_trades": 45,
    "winrate": 64.4,
    "expectancy": 1.1,
    "total_r": 28.0,
    "avg_rr": 2.2,
    "profit_factor": 3.5
  }
]
```

---

#### `GET /stats/by-session`
Statistiques agrégées par session de trading.

**Réponse `200` :** tableau d'objets :
```json
[
  {
    "session": "London",
    "total_trades": 60,
    "winrate": 65.0,
    "expectancy": 1.0,
    "total_r": 32.0,
    "avg_rr": 2.1
  }
]
```

---

#### `GET /stats/daily`
Statistiques journalières.

**Query param supplémentaire :**
| Paramètre | Type | Défaut | Description |
|---|---|---|---|
| `days` | int | `30` | Nombre de jours à inclure (1–365) |

**Réponse `200` :** tableau d'objets :
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

#### `GET /stats/weekly`
Statistiques hebdomadaires.

**Query param supplémentaire :**
| Paramètre | Type | Défaut | Description |
|---|---|---|---|
| `weeks` | int | `12` | Nombre de semaines à inclure (1–52) |

**Réponse `200` :** tableau d'objets :
```json
[
  {
    "week_start": "2024-12-16",
    "week_end": "2024-12-22",
    "total_trades": 12,
    "winning_trades": 8,
    "losing_trades": 4,
    "total_r": 9.0,
    "pnl_usd": 900.0,
    "winrate": 66.7,
    "expectancy": 0.75
  }
]
```

---

#### `GET /stats/errors`
Analyse des erreurs de trading les plus fréquentes.

**Réponse `200` :** tableau d'objets :
```json
[
  {
    "error_type": "FOMO",
    "count": 8,
    "percentage": 22.9,
    "avg_loss_r": -1.3
  }
]
```

---

#### `GET /stats/mental`
Corrélation entre l'état mental (1–5) et les résultats de trading.

**Réponse `200` :** tableau d'objets :
```json
[
  {
    "mental_state": 5,
    "total_trades": 30,
    "winrate": 73.3,
    "avg_result_r": 1.4
  }
]
```

---

#### `GET /stats/equity-curve`
Points de la courbe d'equity, utiles pour visualiser la progression du compte.

**Réponse `200` :** tableau d'objets :
```json
[
  {
    "date": "2024-12-20",
    "cumulative_r": 12.5,
    "cumulative_pnl": 1250.0,
    "trade_count": 15
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
