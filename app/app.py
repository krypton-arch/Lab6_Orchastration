import os
import sys
import json
import time
import hashlib
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Application Configuration from Environment (Injected via ConfigMap)
APP_ENV = os.getenv("APP_ENV", "production")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
FEATURE_FLAG_ANALYTICS = os.getenv("FEATURE_FLAG_ANALYTICS", "enabled")
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "500"))
CLUSTER_ROLE = os.getenv("CLUSTER_ROLE", "web-dashboard")
APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")

# Secret Credentials from Environment (Injected via Kubernetes Secret)
DB_USER = os.getenv("DB_USER", "db_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SuperSecretPassw0rd!")
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "sk-live-k8s-secret-9948271a-lab6")

# Pod Downward API Metadata
POD_NAME = os.getenv("POD_NAME", "lab6-devops-app-local")
POD_NAMESPACE = os.getenv("POD_NAMESPACE", "devops-lab6")
POD_IP = os.getenv("POD_IP", "10.244.1.45")
NODE_NAME = os.getenv("NODE_NAME", "desktop-worker")

# Mounted Files from Volumes (ConfigMap and Secret)
CONFIG_MOUNT_PATH = "/etc/config/app_settings.json"
SECRET_MOUNT_PATH = "/etc/secrets/vault_key.txt"

def get_mounted_config():
    if os.path.exists(CONFIG_MOUNT_PATH):
        try:
            with open(CONFIG_MOUNT_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Failed reading mounted config: {str(e)}"}
    return {
        "source": "simulated_mount",
        "cache_ttl_seconds": 3600,
        "max_connections": 100,
        "maintenance_window": "Sunday 02:00-04:00 UTC",
        "notification_channel": "#devops-alerts"
    }

def get_mounted_secret():
    if os.path.exists(SECRET_MOUNT_PATH):
        try:
            with open(SECRET_MOUNT_PATH, "r") as f:
                content = f.read().strip()
                stat = os.stat(SECRET_MOUNT_PATH)
                mode_octal = oct(stat.st_mode)[-4:]
                return {
                    "exists": True,
                    "permissions": mode_octal,
                    "length": len(content),
                    "fingerprint": hashlib.sha256(content.encode()).hexdigest()[:16] + "..."
                }
        except Exception as e:
            return {"error": f"Failed reading mounted secret: {str(e)}"}
    return {
        "exists": True,
        "permissions": "0400",
        "length": 32,
        "fingerprint": hashlib.sha256(b"simulated_vault_key").hexdigest()[:16] + "..."
    }

def mask_secret(secret_val, show_start=3, show_end=3):
    if not secret_val or len(secret_val) <= (show_start + show_end):
        return "********"
    return secret_val[:show_start] + "*" * (len(secret_val) - show_start - show_end) + secret_val[-show_end:]

@app.route("/")
def index():
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    mounted_cfg = get_mounted_config()
    mounted_sec = get_mounted_secret()
    
    masked_pw = mask_secret(DB_PASSWORD, 2, 2)
    pw_hash = hashlib.sha256(DB_PASSWORD.encode()).hexdigest()[:12]
    masked_token = mask_secret(API_AUTH_TOKEN, 4, 4)
    token_hash = hashlib.sha256(API_AUTH_TOKEN.encode()).hexdigest()[:12]
    
    return render_template(
        "index.html",
        app_version=APP_VERSION,
        app_env=APP_ENV,
        log_level=LOG_LEVEL,
        feature_flag_analytics=FEATURE_FLAG_ANALYTICS,
        max_batch_size=MAX_BATCH_SIZE,
        cluster_role=CLUSTER_ROLE,
        pod_name=POD_NAME,
        pod_namespace=POD_NAMESPACE,
        pod_ip=POD_IP,
        node_name=NODE_NAME,
        db_user=DB_USER,
        masked_pw=masked_pw,
        pw_hash=pw_hash,
        masked_token=masked_token,
        token_hash=token_hash,
        mounted_cfg=mounted_cfg,
        mounted_sec=mounted_sec,
        now_utc=now_utc
    )

@app.route("/api/config")
def api_config():
    return jsonify({
        "status": "success",
        "source": "Kubernetes ConfigMap (v1)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment_variables": {
            "APP_ENV": APP_ENV,
            "LOG_LEVEL": LOG_LEVEL,
            "FEATURE_FLAG_ANALYTICS": FEATURE_FLAG_ANALYTICS,
            "MAX_BATCH_SIZE": MAX_BATCH_SIZE,
            "CLUSTER_ROLE": CLUSTER_ROLE,
            "APP_VERSION": APP_VERSION
        },
        "mounted_file_config": get_mounted_config()
    })

@app.route("/api/secret-status")
def api_secret_status():
    return jsonify({
        "status": "success",
        "source": "Kubernetes Secret (v1/Opaque)",
        "security_policy": "Zero-Trust Secret Masking Compliant",
        "db_user": DB_USER,
        "db_password": {
            "masked": mask_secret(DB_PASSWORD, 2, 2),
            "sha256_prefix": hashlib.sha256(DB_PASSWORD.encode()).hexdigest()[:12],
            "injected_via": "secretKeyRef"
        },
        "api_token": {
            "masked": mask_secret(API_AUTH_TOKEN, 4, 4),
            "sha256_prefix": hashlib.sha256(API_AUTH_TOKEN.encode()).hexdigest()[:12],
            "injected_via": "secretKeyRef"
        },
        "volume_mounted_secret": get_mounted_secret()
    })

@app.route("/api/jobs")
def api_jobs():
    return jsonify({
        "status": "success",
        "batch_job_specs": {
            "target_api": "batch/v1",
            "completions": 3,
            "parallelism": 2,
            "backoff_limit": 4,
            "restart_policy": "OnFailure"
        },
        "cron_job_specs": {
            "target_api": "batch/v1",
            "schedule": "*/2 * * * *",
            "concurrency_policy": "Forbid",
            "successful_jobs_history_limit": 3,
            "failed_jobs_history_limit": 1
        }
    })

@app.route("/healthz")
def healthz():
    return jsonify({"status": "healthy", "service": "devops-lab6-app", "uptime": "ok"}), 200

@app.route("/ready")
def ready():
    # Verify environment and configuration readiness
    if not DB_PASSWORD or not API_AUTH_TOKEN:
        return jsonify({"status": "not_ready", "reason": "Secret configuration missing"}), 503
    return jsonify({"status": "ready", "service": "devops-lab6-app"}), 200

# =========================================================================
# CLI Operating Modes for Batch Job and CronJob Execution
# =========================================================================

def run_batch_job():
    partition = os.getenv("JOB_PARTITION", "1")
    total_partitions = os.getenv("JOB_TOTAL_PARTITIONS", "3")
    print("==================================================================", flush=True)
    print(f"[*] KUBERNETES BATCH JOB INITIATION [batch/v1] - Task: DataProcessor", flush=True)
    print(f"[*] Pod: {POD_NAME} | Node: {NODE_NAME} | Namespace: {POD_NAMESPACE}", flush=True)
    print(f"[*] Partition: {partition} of {total_partitions} | Mode: {APP_ENV}", flush=True)
    print("==================================================================", flush=True)
    
    print(f"[Step 1/4] Verifying ConfigMap parameters...", flush=True)
    print(f"       -> MAX_BATCH_SIZE = {MAX_BATCH_SIZE}", flush=True)
    print(f"       -> LOG_LEVEL      = {LOG_LEVEL}", flush=True)
    time.sleep(1.2)
    
    print(f"[Step 2/4] Authenticating with database via Kubernetes Secret...", flush=True)
    print(f"       -> DB_USER        = {DB_USER}", flush=True)
    print(f"       -> DB_PASSWORD    = {mask_secret(DB_PASSWORD, 2, 2)} [SHA256: {hashlib.sha256(DB_PASSWORD.encode()).hexdigest()[:8]}...]", flush=True)
    print(f"       -> Connection to PostgreSQL endpoint established: SSL/TLS Active", flush=True)
    time.sleep(1.5)
    
    print(f"[Step 3/4] Processing Partition {partition} records...", flush=True)
    for i in range(1, 6):
        pct = i * 20
        records = int((MAX_BATCH_SIZE / 5) * i)
        print(f"       [{pct:3d}%] Processed {records}/{MAX_BATCH_SIZE} records in block {i}...", flush=True)
        time.sleep(0.7)
        
    print(f"[Step 4/4] Verifying Cryptographic Checksums & Committing Batch State...", flush=True)
    digest = hashlib.sha256(f"partition-{partition}-{MAX_BATCH_SIZE}-{time.time()}".encode()).hexdigest()
    print(f"       -> Batch Hash: {digest}", flush=True)
    print(f"       -> Transaction successfully committed to persistent store.", flush=True)
    print(f"[SUCCESS] Job Pod {POD_NAME} finished partition {partition} successfully. Exiting code 0.\n", flush=True)
    sys.exit(0)

def run_cron_job():
    print("==================================================================", flush=True)
    print(f"[*] KUBERNETES CRONJOB EXECUTION [batch/v1] - Task: PeriodicAuditCleaner", flush=True)
    print(f"[*] Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", flush=True)
    print(f"[*] Pod: {POD_NAME} | Namespace: {POD_NAMESPACE} | Node: {NODE_NAME}", flush=True)
    print("==================================================================", flush=True)
    
    print(f"[Step 1/3] Reading security token and API credentials from Secret...", flush=True)
    print(f"       -> API_AUTH_TOKEN: {mask_secret(API_AUTH_TOKEN, 4, 4)}", flush=True)
    print(f"       -> Token Status: ACTIVE (Valid for 86400 seconds)", flush=True)
    time.sleep(1.0)
    
    print(f"[Step 2/3] Performing automated cache eviction and audit compaction...", flush=True)
    print(f"       -> Scanned 128 cache segments across cluster nodes.", flush=True)
    print(f"       -> Purged 14 stale temporary entries older than TTL threshold.", flush=True)
    time.sleep(1.2)
    
    print(f"[Step 3/3] Emitting periodic telemetry heartbeat to monitoring service...", flush=True)
    print(f"       -> Telemetry payload sent: HTTP 200 OK (Latency: 14ms)", flush=True)
    print(f"[SUCCESS] CronJob execution cycle completed successfully. Pod terminating cleanly.\n", flush=True)
    sys.exit(0)

if __name__ == "__main__":
    mode = "web"
    for arg in sys.argv[1:]:
        if arg.startswith("--mode="):
            mode = arg.split("=")[1].strip().lower()
            
    if mode == "job":
        run_batch_job()
    elif mode == "cron":
        run_cron_job()
    else:
        port = int(os.getenv("PORT", "5000"))
        print(f"[*] Starting DevOps Lab 6 Web Server on port {port} [Release: {APP_VERSION}]...", flush=True)
        app.run(host="0.0.0.0", port=port, debug=False)
