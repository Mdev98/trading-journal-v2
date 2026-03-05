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

> 🔒 Les endpoints marqués **[Auth]** nécessitent l'en-tête HTTP `X-Owner-Key`.
> La documentation interactive complète est disponible sur http://localhost:8000/docs

---

### Trades

#### `POST /trades` — Créer un trade 🔒

**Entrée** — Corps JSON (`application/json`) :

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `date` | datetime | ✅ | Date/heure du trade (ISO 8601) |
| `instrument` | string | ✅ | Instrument tradé (ex. `XAUUSD`) |
| `session` | string | ✅ | Session : `Asia`, `London`, `NY`, `Overlap` |
| `setup` | string | ✅ | Setup utilisé (ex. `CRT`, `BOS`) |
| `direction` | string | ✅ | `Buy` ou `Sell` |
| `timeframe` | string | ✅ | Unité de temps (ex. `M15`, `H1`) |
| `entry` | float | ✅ | Prix d'entrée |
| `stop_loss` | float | ✅ | Niveau de stop loss |
| `take_profit` | float | ➖ | Niveau de take profit |
| `risk_pct` | float | ✅ | Risque en % du capital |
| `risk_usd` | float | ✅ | Risque en USD |
| `rr_expected` | float | ✅ | Risk/Reward attendu |
| `result_r` | float | ➖ | Résultat en R (positif = gain, négatif = perte) |
| `pnl_usd` | float | ➖ | P&L en USD |
| `duration_min` | int | ➖ | Durée du trade en minutes |
| `respected_plan` | bool | ➖ | Plan respecté ? (défaut : `true`) |
| `error` | bool | ➖ | Erreur commise ? (défaut : `false`) |
| `error_type` | string | ➖ | Type d'erreur : `None`, `FOMO`, `Revenge`, `Oversize`, `No SL`, `Early Exit`, `Late Entry`, `Wrong Setup`, `News Ignored`, `Overtrading`, `Other` |
| `mental_state` | int | ➖ | État mental de 1 (mauvais) à 5 (excellent) |
| `notes` | string | ➖ | Notes libres |

**Sortie** — `201 Created` : objet `TradeResponse` (voir ci-dessous).

---

#### `GET /trades` — Lister les trades

**Entrée** — Paramètres de requête (query params) :

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `page` | int | `1` | Numéro de page (min : 1) |
| `page_size` | int | `20` | Résultats par page (1–100) |
| `instrument` | string | — | Filtrer par instrument (ex. `XAUUSD`) |
| `session` | string | — | Filtrer par session |
| `setup` | string | — | Filtrer par setup |
| `direction` | string | — | Filtrer par direction (`Buy` / `Sell`) |
| `date_from` | datetime | — | Date de début (ISO 8601) |
| `date_to` | datetime | — | Date de fin (ISO 8601) |
| `is_winner` | bool | — | `true` = gagnants uniquement, `false` = perdants |

**Sortie** — `200 OK` :

```json
{
  "trades": [ /* liste de TradeResponse */ ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

#### `GET /trades/filters` — Options de filtrage

**Entrée** — Aucune.

**Sortie** — `200 OK` :

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

**Entrée** — Paramètre de chemin :

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | int | Identifiant du trade |

**Sortie** — `200 OK` : objet `TradeResponse` (voir ci-dessous). `404` si le trade est introuvable.

---

#### `PUT /trades/{id}` — Modifier un trade 🔒

**Entrée** — Paramètre de chemin `id` (int) + corps JSON (tous les champs sont optionnels, identiques à `POST /trades`).

**Sortie** — `200 OK` : objet `TradeResponse` mis à jour. `404` si introuvable.

---

#### `DELETE /trades/{id}` — Supprimer un trade 🔒

**Entrée** — Paramètre de chemin :

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | int | Identifiant du trade à supprimer |

**Sortie** — `204 No Content`. Supprime également toutes les images associées. `404` si introuvable.

---

#### 📦 Objet `TradeResponse`

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
  "created_at": "2024-12-20T10:35:00",
  "updated_at": "2024-12-20T10:35:00",
  "is_winner": true,
  "is_loser": false,
  "is_breakeven": false,
  "images": [ /* liste de TradeImageResponse */ ]
}
```

---

### Images

#### `POST /trades/{id}/images` — Upload d'images 🔒

**Entrée** — Paramètre de chemin `id` (int) + corps `multipart/form-data` :

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `files` | fichier(s) | ✅ | Images à uploader (max 10 ; formats : JPG, PNG, GIF, WebP ; taille max : 10 MB) |
| `image_type` | string | ➖ | `before`, `during`, `after`, `analysis` (défaut : `analysis`) |
| `caption` | string | ➖ | Légende de l'image |

**Sortie** — `201 Created` : liste d'objets `TradeImageResponse`.

```json
[
  {
    "id": 5,
    "trade_id": 1,
    "image_url": "/uploads/1/abc123.png",
    "image_type": "before",
    "caption": "Setup avant entrée",
    "created_at": "2024-12-20T10:36:00"
  }
]
```

---

#### `GET /trades/{id}/images` — Liste des images d'un trade

**Entrée** — Paramètre de chemin :

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | int | Identifiant du trade |

**Sortie** — `200 OK` : liste d'objets `TradeImageResponse` (même format que ci-dessus). `404` si le trade est introuvable.

---

#### `DELETE /trades/images/{id}` — Supprimer une image 🔒

**Entrée** — Paramètre de chemin :

| Paramètre | Type | Description |
|-----------|------|-------------|
| `id` | int | Identifiant de l'image |

**Sortie** — `204 No Content`. Supprime le fichier (Supabase ou local). `404` si introuvable.

---

### Statistiques

> Tous les endpoints de stats acceptent les **filtres communs** suivants via query params :
>
> | Paramètre | Type | Description |
> |-----------|------|-------------|
> | `date_from` | datetime | Date de début |
> | `date_to` | datetime | Date de fin |
> | `instrument` | string | Filtrer par instrument |
> | `setup` | string | Filtrer par setup |

---

#### `GET /stats/global` — Statistiques globales

**Entrée** — Filtres communs (optionnels).

**Sortie** — `200 OK` :

```json
{
  "total_trades": 100,
  "winning_trades": 55,
  "losing_trades": 40,
  "breakeven_trades": 5,
  "winrate": 55.0,
  "avg_win_r": 2.1,
  "avg_loss_r": -1.0,
  "expectancy": 0.75,
  "profit_factor": 1.8,
  "total_pnl_usd": 3500.0,
  "total_r": 75.0,
  "max_drawdown_r": -8.5,
  "max_drawdown_pct": 4.2,
  "avg_rr_expected": 2.5,
  "avg_rr_actual": 1.9,
  "discipline_rate": 88.0,
  "avg_duration_min": 37.5
}
```

---

#### `GET /stats/by-setup` — Statistiques par setup

**Entrée** — Filtres communs (optionnels).

**Sortie** — `200 OK` : liste triée par performance décroissante (`total_r`) :

```json
[
  {
    "setup": "CRT",
    "total_trades": 40,
    "winrate": 60.0,
    "expectancy": 0.9,
    "total_r": 36.0,
    "avg_rr": 2.2,
    "profit_factor": 2.1
  }
]
```

---

#### `GET /stats/by-session` — Statistiques par session

**Entrée** — Filtres communs (optionnels).

**Sortie** — `200 OK` :

```json
[
  {
    "session": "London",
    "total_trades": 50,
    "winrate": 58.0,
    "expectancy": 0.8,
    "total_r": 40.0,
    "avg_rr": 2.0
  }
]
```

---

#### `GET /stats/daily` — Statistiques journalières

**Entrée** — Filtres communs + :

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `days` | int | `30` | Nombre de jours à inclure (1–365) |

**Sortie** — `200 OK` :

```json
[
  {
    "date": "2024-12-20",
    "total_trades": 3,
    "winning_trades": 2,
    "losing_trades": 1,
    "total_r": 3.0,
    "pnl_usd": 300.0,
    "winrate": 66.7
  }
]
```

---

#### `GET /stats/weekly` — Statistiques hebdomadaires

**Entrée** — Filtres communs + :

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `weeks` | int | `12` | Nombre de semaines à inclure (1–52) |

**Sortie** — `200 OK` :

```json
[
  {
    "week_start": "2024-12-16",
    "week_end": "2024-12-22",
    "total_trades": 10,
    "winning_trades": 6,
    "losing_trades": 4,
    "total_r": 8.5,
    "pnl_usd": 850.0,
    "winrate": 60.0,
    "expectancy": 0.85
  }
]
```

---

#### `GET /stats/errors` — Analyse des erreurs

**Entrée** — Filtres communs (optionnels).

**Sortie** — `200 OK` :

```json
[
  {
    "error_type": "FOMO",
    "count": 12,
    "percentage": 34.3,
    "avg_loss_r": -1.5
  }
]
```

---

#### `GET /stats/mental` — Corrélation état mental / résultats

**Entrée** — Filtres communs (optionnels).

**Sortie** — `200 OK` :

```json
[
  {
    "mental_state": 4,
    "total_trades": 25,
    "winrate": 64.0,
    "avg_result_r": 1.2
  }
]
```

---

#### `GET /stats/equity-curve` — Courbe d'equity

**Entrée** — Filtres communs (optionnels).

**Sortie** — `200 OK` : liste de points chronologiques :

```json
[
  {
    "date": "2024-12-20",
    "cumulative_r": 75.0,
    "cumulative_pnl": 7500.0,
    "trade_count": 100
  }
]
```

---

### Stockage

#### `GET /trades/storage/status` — Statut du stockage

**Entrée** — Aucune.

**Sortie** — `200 OK` :

```json
{
  "storage_type": "supabase",
  "supabase_configured": true
}
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
