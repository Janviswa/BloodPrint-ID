# gunicorn.conf.py — Memory-safe config for Render free tier (512 MB RAM)
import os

# FIX 2: OOM ("perhaps out of memory") on Render.
#
# Root cause: default gunicorn spawns (2 * CPU + 1) workers.
# On Render free tier that's typically 3 workers. Each worker loads
# the full TFLite model + OpenCV into memory independently.
# EfficientNet-B0 TFLite ≈ 17 MB on disk but expands to ~150 MB in RAM.
# 3 workers × 150 MB = 450 MB → OOM on 512 MB instance.
#
# Fix: 1 worker only, 4 threads for concurrency.
# The model is loaded once (lazy singleton in predictor.py) and shared.

workers    = 1          # single worker = single model copy in RAM
threads    = 4          # handle concurrent requests via threads
worker_class = "gthread"

# Recycle worker after N requests to prevent slow memory leaks
max_requests        = 500
max_requests_jitter = 50

# Generous timeout for first request (model cold-load can take ~10s)
timeout  = 120
graceful_timeout = 30

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Pre-load the app so the model is loaded before workers fork
# (saves RAM on multi-worker setups if you ever scale up)
preload_app = True

# Logging
accesslog  = "-"
errorlog   = "-"
loglevel   = "info"
