# MedPeer - Full Ready (S3 + SocketIO) Starter

This project is a deploy-ready Flask app implementing a social network for medical students with S3 file storage and real-time messaging via Socket.IO.

## Quick overview
- Flask backend with SQLAlchemy models (Postgres recommended)
- File uploads stored on S3 (or S3-compatible service)
- Real-time one-to-one messaging with Flask-SocketIO (Eventlet worker on Gunicorn)
- Admin accounts seeded via `seed_dev.py`
- Dark/light preference saved per-user
- Basic search (SQL LIKE)
- Prepared for Render deployment (Procfile included)

## What you must provide (env vars)
Copy `.env.example` to `.env` and populate values before deploying:
- SECRET_KEY
- DATABASE_URL (Postgres URI)
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_REGION
- REDIS_URL (optional for message queue / Celery later)
- MAIL_... (optional)

## Local development (simple)
1. Create virtualenv python 3.10+
2. pip install -r requirements.txt
3. export env vars or copy .env.example to .env and edit
4. flask db upgrade
5. python seed_dev.py
6. flask run

## Deploy to Render
- Create Web Service: connect your GitHub repo
- Set Build Command: `pip install -r requirements.txt`
- Start Command (Procfile used) example: `gunicorn -k eventlet -w 1 wsgi:app`
- Add Postgres and set `DATABASE_URL`
- Add env vars (AWS keys, SECRET_KEY, etc.)
- Run migrations and seed via Render Shell (flask db upgrade; python seed_dev.py)

## Notes & next steps
- This is a deployable full-stack starter. For heavy production use, add further tests, rate-limiting, virus scanning, content moderation UIs, and monitoring.
