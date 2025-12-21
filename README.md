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

### Trades
- `POST /trades` - Créer un trade
- `GET /trades` - Lister les trades (avec pagination et filtres)
- `GET /trades/{id}` - Détail d'un trade
- `PUT /trades/{id}` - Modifier un trade
- `DELETE /trades/{id}` - Supprimer un trade
- `GET /trades/filters` - Options de filtrage

### Images
- `POST /trades/{id}/images` - Upload d'images
- `GET /trades/{id}/images` - Liste des images
- `DELETE /trades/images/{id}` - Supprimer une image

### Statistiques
- `GET /stats/global` - Stats globales
- `GET /stats/by-setup` - Stats par setup
- `GET /stats/by-session` - Stats par session
- `GET /stats/daily` - Stats journalières
- `GET /stats/weekly` - Stats hebdomadaires
- `GET /stats/errors` - Analyse des erreurs
- `GET /stats/mental` - Corrélation état mental
- `GET /stats/equity-curve` - Courbe d'equity

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
