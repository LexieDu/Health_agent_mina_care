# choose correct python env
cd Health-Agent-mina_care
source venv/bin/activate
pip install -r ./backend/requirements.txt
python3 -m pip install -r ./backend/requirements.txt

# Terminal 1 - Backend (restart to load new endpoint)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
python3 -m http.server 3000

# Test standalone (optional)
cd backend/agents
python mina_agent.py