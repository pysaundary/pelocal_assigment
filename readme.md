text
AI Generated hai yeh thik hai 


# Pysaundary Todo (FastAPI + Vanilla JS)

Mint-themed login/signup and tasks CRUD using FastAPI (SQLite, JWT) and Bootstrap with inline JavaScript.

## Quick Start

1) Clone
git clone <your-repo-url>
cd pelocal_assigment

text

2) Create venv

Linux/macOS:
python3 -m venv venv
source venv/bin/activate

text

Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

text

Windows (CMD):
python -m venv venv
venv\Scripts\activate.bat

text

3) Install deps (if applicable)
pip install -r requirements.txt

text

4) Run server
python backend/launch.py

text
Open:
- http://0.0.0.0:8000/  (Auth page)
- http://0.0.0.0:8000/tasks  (Tasks page)

## Frontend files

- backend/static/index.html  (Login/Signup with inline JS)
- backend/static/tasks.html  (Tasks CRUD with inline JS)

Both files call the API via:
const API_BASE = 'http://0.0.0.0:8000';

text

## Deploy note

Server par deploy karte waqt in dono files me API base ko apne server ke IP/host + port se replace kar do:

- backend/static/index.html
- backend/static/tasks.html

Example:
// before
const API_BASE = 'http://0.0.0.0:8000';

// after
const API_BASE = 'http://<SERVER_IP_OR_HOST>:<PORT>';
// e.g. http://123.45.67.89:8000 or https://app.example.com

text

CORS: launch.py me CORSMiddleware abhi permissive hai (allow_origins=["*"]). Zaroorat ho to production me apne origin tak restrict kar sakte ho.

## Common issues

- 404 at /index.html: Root page “/” use karo; tasks “/tasks” pe served hai. Static assets sirf /static ke niche serve hote hain.
- HTTPS deploy: API_BASE ko https origin pe set karo, warna browser mixed-content block karega.