# TruthTube Backend

YouTube video quality analyzer using AI.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/analyze` - Analyze YouTube videos
