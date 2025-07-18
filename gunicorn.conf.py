# === CONFIGURAÇÃO GUNICORN PARA HOSTINGER ===
# Arquivo de configuração para servidor web de produção

import os

# === CONFIGURAÇÕES BÁSICAS ===
bind = "0.0.0.0:8000"  # Porta pode variar conforme Hostinger
workers = int(os.environ.get('WEB_CONCURRENCY', 2))
timeout = int(os.environ.get('TIMEOUT', 120))
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# === CONFIGURAÇÕES DE PERFORMANCE ===
worker_class = "sync"
worker_connections = 1000
preload_app = True

# === LOGS ===
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"

# === CONFIGURAÇÕES DE PROCESSO ===
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# === HOOKS ===
def on_starting(server):
    server.log.info("🚀 Iniciando L7Nutri em produção...")

def on_reload(server):
    server.log.info("🔄 Recarregando aplicação...")

def worker_int(worker):
    worker.log.info("🛑 Worker interrompido por sinal")

def pre_fork(server, worker):
    server.log.info(f"👷 Worker {worker.pid} sendo criado")

def post_fork(server, worker):
    server.log.info(f"✅ Worker {worker.pid} pronto")

def when_ready(server):
    server.log.info("🎉 L7Nutri pronto para receber requisições!")

def worker_abort(worker):
    worker.log.info(f"💥 Worker {worker.pid} abortado")

# === CONFIGURAÇÕES DE SEGURANÇA ===
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
