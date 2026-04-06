"""Gunicorn configuration for Render deployment."""
import os
import multiprocessing

# Bind to the port Render provides
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"

# Use uvicorn workers
worker_class = "uvicorn.workers.UvicornWorker"

# Single worker for memory efficiency on free tier
workers = 1

# Timeout for slow startup (10 minutes to allow for model loading)
timeout = 600

# Graceful timeout
graceful_timeout = 30

# Keepalive
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Don't preload - bind to port FIRST, then load worker
preload_app = False

# Use the startup script that handles all the logic
factory = False  # app:app is not a factory, it's the app object

def on_starting(server):
    """Called just before the master process is initialized."""
    print(f"[GUNICORN] Starting on {bind}", flush=True)


def on_reload(server):
    """Called when worker is reloaded."""
    print(f"[GUNICORN] Reloading workers", flush=True)


def when_ready(server):
    """Called just after the server is started."""
    print(f"[GUNICORN] Server is ready. Accepting connections.", flush=True)
