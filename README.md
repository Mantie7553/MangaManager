# MangaManager

A personal manga collection tracker with a visual bookshelf UI. Track series and volumes, upload cover art, mark favorites, and surface missing volumes at a glance.

## Stack

- **Frontend**: Vue 3 + TypeScript + Vite + Tailwind CSS v4
- **Backend**: FastAPI + SQLAlchemy + SQLite

## Project Structure
```
MangaManager/
├── frontend/       # Vue 3 app
└── backend/
    └── api/        # FastAPI app
```

## Setup

### Backend

```bash
cd backend/api
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

Create a `.env` file in `backend/api/`:

```
DATABASE_URL=sqlite:///./manga.db
```

Start the server:
```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

## Features

- Visual bookshelf UI with cover art
- Add/edit/delete series and volumes
- Upload cover images (per-series folder structure)
- Missing volume detection with gap highlighting
- Favorite series and volumes
- Search and sort
- Right-click context menus
- Mobile-responsive layout