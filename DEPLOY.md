# Deploying MedPeer to Render (short guide)

1. Push the repo to GitHub.
2. Create a new Web Service on Render pointing to the repo.
3. Add Postgres addon and set `DATABASE_URL` env var on Render.
4. Add required env vars (SECRET_KEY, AWS keys, AWS_STORAGE_BUCKET_NAME, AWS_REGION).
5. Ensure build command installs dependencies (requirements.txt).
6. Start command: Gunicorn will read Procfile; ensure worker type eventlet if using SocketIO:
   `gunicorn -k eventlet -w 1 wsgi:app`
7. Open Shell on Render, run `flask db upgrade` and `python seed_dev.py`.
8. Done — visit your deployed site.
