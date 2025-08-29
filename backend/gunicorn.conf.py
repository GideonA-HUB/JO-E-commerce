"""
Gunicorn configuration for TASTY FINGERS
Optimized to prevent unwanted 301 redirects
"""
import os
import multiprocessing

# Server socket
bind = "0.0.0.0:3000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 0
max_requests_jitter = 0
timeout = 120
graceful_timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "tasty-fingers"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload app for better performance
preload_app = True

def on_starting(server):
    """Log server startup"""
    server.log.info("🚀 Starting TASTY FINGERS server...")

def on_reload(server):
    """Log server reload"""
    server.log.info("🔄 Reloading TASTY FINGERS server...")

def when_ready(server):
    """Log when server is ready"""
    server.log.info("✅ TASTY FINGERS server is ready!")

def pre_fork(server, worker):
    """Log before forking worker"""
    server.log.info(f"🔧 Forking worker {worker.pid}")

def post_fork(server, worker):
    """Log after forking worker"""
    server.log.info(f"✅ Worker {worker.pid} forked")

def post_worker_init(worker):
    """Log after worker initialization"""
    worker.log.info(f"🎯 Worker {worker.pid} initialized")

def worker_int(worker):
    """Log worker interrupt"""
    worker.log.info(f"⚠️ Worker {worker.pid} received INT signal")

def worker_abort(worker):
    """Log worker abort"""
    worker.log.info(f"❌ Worker {worker.pid} received ABORT signal")

def pre_exec(server):
    """Log before exec"""
    server.log.info("🔄 Server about to exec")

def pre_request(worker, req):
    """Log before request processing"""
    worker.log.debug(f"📥 {req.method} {req.path}")

def post_request(worker, req, environ, resp):
    """Log after request processing"""
    worker.log.debug(f"📤 {req.method} {req.path} -> {resp.status}")

def child_exit(server, worker):
    """Log child exit"""
    server.log.info(f"👋 Worker {worker.pid} exited")

def worker_exit(server, worker):
    """Log worker exit"""
    server.log.info(f"👋 Worker {worker.pid} exited")

def nworkers_changed(server, new_value, old_value):
    """Log when number of workers changes"""
    server.log.info(f"🔄 Workers changed from {old_value} to {new_value}")

def on_exit(server):
    """Log server exit"""
    server.log.info("👋 TASTY FINGERS server shutting down")

def ssl_context(server):
    """SSL context (if needed)"""
    return None

# Proxy settings for Railway/Heroku
forwarded_allow_ips = ['127.0.0.1', '::1']
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
