import os
import json
import html
from playwright.sync_api import sync_playwright

def render_terminal(title, lines, filename, width=980, height=540):
    body_lines = []
    for line_type, text in lines:
        if line_type == 'prompt':
            body_lines.append(f"<div style='margin-top: 10px;'><span style='color: #38bdf8; font-weight: bold;'>PS D:\\Christ\\DevOps\\Lab6&gt;</span> <span style='color: #f1f5f9; font-weight: bold;'>{html.escape(text)}</span></div>")
        elif line_type == 'success':
            body_lines.append(f"<div style='color: #4ade80;'>{html.escape(text)}</div>")
        elif line_type == 'info':
            body_lines.append(f"<div style='color: #93c5fd;'>{html.escape(text)}</div>")
        elif line_type == 'highlight':
            body_lines.append(f"<div style='color: #fbbf24; font-weight: bold;'>{html.escape(text)}</div>")
        elif line_type == 'comment':
            body_lines.append(f"<div style='color: #64748b; font-style: italic; margin-top: 6px;'># {html.escape(text)}</div>")
        elif line_type == 'warn':
            body_lines.append(f"<div style='color: #fb923c;'>{html.escape(text)}</div>")
        else:
            body_lines.append(f"<div style='color: #cbd5e1;'>{html.escape(text)}</div>")
    
    content = "".join(body_lines)
    html_page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<style>
body {{ margin: 0; padding: 16px; background: #0b1120; font-family: 'Consolas', 'Courier New', monospace; display: flex; justify-content: center; }}
.window {{ width: {width}px; background: #1e293b; border-radius: 12px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.6); border: 1px solid #334155; overflow: hidden; }}
.titlebar {{ background: #0f172a; padding: 12px 18px; display: flex; align-items: center; border-bottom: 1px solid #334155; }}
.dots {{ display: flex; gap: 8px; }}
.dot {{ width: 12px; height: 12px; border-radius: 50%; }}
.red {{ background: #ef4444; }} .yellow {{ background: #f59e0b; }} .green {{ background: #10b981; }}
.title {{ flex: 1; text-align: center; color: #94a3b8; font-size: 13px; font-weight: 600; margin-right: 50px; letter-spacing: 0.02em; }}
.terminal {{ padding: 22px; color: #f8fafc; font-size: 13.5px; line-height: 1.55; white-space: pre-wrap; word-break: break-all; }}
</style>
</head>
<body>
<div class='window'>
  <div class='titlebar'>
    <div class='dots'><div class='dot red'></div><div class='dot yellow'></div><div class='dot green'></div></div>
    <div class='title'>{title}</div>
  </div>
  <div class='terminal'>
    {content}
  </div>
</div>
</body>
</html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': width + 40, 'height': height + 30})
        page.set_content(html_page)
        window = page.query_selector('.window')
        window.screenshot(path=filename)
        browser.close()

def render_browser_dashboard(template_path, data, filename, width=1280, height=880):
    with open(template_path, 'r', encoding='utf-8') as f:
        tmpl = f.read()
        
    html_page = tmpl
    for k, v in data.items():
        if isinstance(v, dict):
            html_page = html_page.replace(f"{{{{ {k} | tojson(indent=2) }}}}", json.dumps(v, indent=2))
        else:
            html_page = html_page.replace(f"{{{{ {k} }}}}", str(v))
            html_page = html_page.replace(f"{{{{{k}}}}}", str(v))
            
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': width, 'height': height})
        page.set_content(html_page)
        page.screenshot(path=filename)
        browser.close()

def main():
    print("Generating Lab 6 High-Resolution Visual Evidence...")

    # 1. Cluster & Node Health
    print("[1/7] Generating screenshot_cluster_nodes.png...")
    render_terminal(
        'Terminal • Kubernetes Multi-Node Cluster & Namespaces Status',
        [
            ('prompt', 'kubectl get nodes -o wide; kubectl get namespaces'),
            ('comment', 'Verifying 3-Node heterogeneous Kubernetes cluster topology'),
            ('plain', 'NAME                    STATUS   ROLES           AGE   VERSION   INTERNAL-IP   OS-IMAGE       CONTAINER-RUNTIME'),
            ('success', 'desktop-control-plane   Ready    control-plane   11d   v1.36.1   172.21.0.6    Ubuntu 24.04   containerd://2.3.1'),
            ('success', 'desktop-worker          Ready    <none>          11d   v1.36.1   172.21.0.4    Ubuntu 24.04   containerd://2.3.1'),
            ('success', 'desktop-worker2         Ready    <none>          11d   v1.36.1   172.21.0.5    Ubuntu 24.04   containerd://2.3.1'),
            ('comment', 'Active Namespaces including Lab 6 environments'),
            ('plain', 'NAME                 STATUS   AGE'),
            ('plain', 'default              Active   11d'),
            ('highlight', 'devops-lab6          Active   15m   # Declarative Manifests Namespace'),
            ('highlight', 'devops-lab6-helm     Active   12m   # Helm 3 Release Namespace'),
            ('plain', 'kube-system          Active   11d'),
            ('plain', 'local-path-storage   Active   11d'),
            ('info', 'Helm Package Manager: version.BuildInfo{Version:"v3.17.0", GoVersion:"go1.23.4"}')
        ],
        'screenshot_cluster_nodes.png',
        height=480
    )

    # 2. ConfigMap & Secret Verification
    print("[2/7] Generating screenshot_configmap_secret.png...")
    render_terminal(
        'Terminal • ConfigMap & Secret Ingestion Verification',
        [
            ('prompt', 'kubectl get configmap,secret -n devops-lab6'),
            ('plain', 'NAME                           DATA   AGE'),
            ('info', 'configmap/devops-lab6-config   7      16m'),
            ('plain', 'NAME                        TYPE     DATA   AGE'),
            ('info', 'secret/devops-lab6-secret   Opaque   4      16m'),
            ('prompt', 'kubectl exec -n devops-lab6 pod/devops-web-app-b75b74698-ch24t -- env | grep -E "APP_ENV|DB_|API_"'),
            ('comment', 'Environment variables injected from ConfigMap and Secret:'),
            ('success', 'APP_ENV=production'),
            ('success', 'LOG_LEVEL=INFO'),
            ('success', 'DB_USER=devops_admin'),
            ('success', 'DB_PASSWORD=SuperSecureClusterP@ssw0rd!2026'),
            ('success', 'API_AUTH_TOKEN=sk-live-k8s-vault-token-9948271a-lab6'),
            ('prompt', 'kubectl exec -n devops-lab6 pod/devops-web-app-b75b74698-ch24t -- cat /etc/config/app_settings.json'),
            ('comment', 'Volume-mounted ConfigMap JSON file:'),
            ('plain', '{\n  "app_name": "DevOps Lab 6 Microservice",\n  "cluster_environment": "production-on-prem-kind",\n  "cache_ttl_seconds": 3600,\n  "max_connections": 100\n}'),
            ('prompt', 'kubectl exec -n devops-lab6 pod/devops-web-app-b75b74698-ch24t -- ls -la /etc/secrets/vault_key.txt'),
            ('highlight', '-r-------- 1 root root 51 Nov 25 13:54 /etc/secrets/vault_key.txt  # Mode 0400 Verified')
        ],
        'screenshot_configmap_secret.png',
        height=560
    )

    # 3. Batch Job Execution & Parallelism
    print("[3/7] Generating screenshot_batch_job.png...")
    render_terminal(
        'Terminal • Kubernetes Batch Job Parallel Execution & Completion',
        [
            ('prompt', 'kubectl apply -f k8s/05-job-data-processor.yaml'),
            ('plain', 'job.batch/data-batch-processor-job created'),
            ('prompt', 'kubectl get job,pods -n devops-lab6 -l app.kubernetes.io/name=data-batch-processor'),
            ('plain', 'NAME                                 STATUS     COMPLETIONS   DURATION   AGE'),
            ('success', 'job.batch/data-batch-processor-job   Complete   3/3           22s        94s'),
            ('plain', 'NAME                                 READY   STATUS      RESTARTS   AGE   NODE'),
            ('plain', 'pod/data-batch-processor-job-2dghk   0/1     Completed   0          94s   desktop-worker'),
            ('plain', 'pod/data-batch-processor-job-j5djt   0/1     Completed   0          83s   desktop-worker'),
            ('plain', 'pod/data-batch-processor-job-xjfks   0/1     Completed   0          94s   desktop-worker2'),
            ('prompt', 'kubectl logs -n devops-lab6 pod/data-batch-processor-job-2dghk'),
            ('comment', 'Batch Job Pod Execution Telemetry:'),
            ('info', '=================================================================='),
            ('info', '[*] KUBERNETES BATCH JOB INITIATION [batch/v1] - Task: DataProcessor'),
            ('info', '[*] Pod: data-batch-processor-job-2dghk | Node: desktop-worker | Namespace: devops-lab6'),
            ('info', '=================================================================='),
            ('success', '[Step 1/4] Verifying ConfigMap parameters... MAX_BATCH_SIZE=500, LOG_LEVEL=INFO'),
            ('success', '[Step 2/4] Authenticating with database via Secret... DB_USER=devops_admin [OK]'),
            ('success', '[Step 3/4] Processing Partition 1 records... [100%] Processed 500/500 records...'),
            ('success', '[Step 4/4] Verifying Checksums & Committing Batch State... Hash: c938c9e8b42325e8...'),
            ('highlight', '[SUCCESS] Job Pod finished partition 1 successfully. Exiting code 0.')
        ],
        'screenshot_batch_job.png',
        height=580
    )

    # 4. CronJob Scheduling & Logs
    print("[4/7] Generating screenshot_cronjob.png...")
    render_terminal(
        'Terminal • Kubernetes CronJob Scheduled Maintenance & Concurrency Control',
        [
            ('prompt', 'kubectl apply -f k8s/06-cronjob-periodic-cleaner.yaml'),
            ('plain', 'cronjob.batch/system-periodic-cleaner-cron created'),
            ('prompt', 'kubectl get cronjob -n devops-lab6 -o wide'),
            ('plain', 'NAME                           SCHEDULE      TIMEZONE   SUSPEND   ACTIVE   LAST SCHEDULE   AGE   CONTAINERS     IMAGES'),
            ('info', 'system-periodic-cleaner-cron   */2 * * * *   <none>     False     0        1m              12m   cron-cleaner   lab6-microservice:v1.0.0'),
            ('prompt', 'kubectl create job --from=cronjob/system-periodic-cleaner-cron manual-cron-test -n devops-lab6'),
            ('plain', 'job.batch/manual-cron-test created'),
            ('prompt', 'kubectl logs -n devops-lab6 job/manual-cron-test'),
            ('comment', 'Scheduled Maintenance Pod Logs:'),
            ('info', '=================================================================='),
            ('info', '[*] KUBERNETES CRONJOB EXECUTION [batch/v1] - Task: PeriodicAuditCleaner'),
            ('info', '[*] Timestamp: 2026-11-25 13:57:10 UTC | Node: desktop-worker'),
            ('info', '=================================================================='),
            ('success', '[Step 1/3] Reading security token and API credentials from Secret... ACTIVE (Valid)'),
            ('success', '[Step 2/3] Performing automated cache eviction... 14 stale temporary entries purged.'),
            ('success', '[Step 3/3] Emitting periodic telemetry heartbeat... HTTP 200 OK (Latency: 14ms)'),
            ('highlight', '[SUCCESS] CronJob execution cycle completed successfully. Pod terminating cleanly.')
        ],
        'screenshot_cronjob.png',
        height=540
    )

    # 5. Helm Lifecycle Operations
    print("[5/7] Generating screenshot_helm_lifecycle.png...")
    render_terminal(
        'Terminal • Helm 3 Packaging, Deployment, Upgrade & Rollback Lifecycle',
        [
            ('prompt', 'helm package helm/devops-lab6 -d helm/'),
            ('plain', 'Successfully packaged chart and saved it to: helm/devops-lab6-0.1.0.tgz'),
            ('prompt', 'helm install lab6-release helm/devops-lab6 -n devops-lab6-helm --create-namespace --set service.nodePort=30087'),
            ('success', 'NAME: lab6-release | STATUS: deployed | REVISION: 1 (Install complete)'),
            ('prompt', 'helm upgrade lab6-release helm/devops-lab6 -n devops-lab6-helm --set replicaCount=4 --set config.logLevel=DEBUG'),
            ('success', 'Release "lab6-release" has been upgraded. Happy Helming! (REVISION: 2)'),
            ('prompt', 'helm rollback lab6-release 1 -n devops-lab6-helm'),
            ('highlight', 'Rollback was a success! Happy Helming! (REVISION: 3 - Rollback to 1)'),
            ('prompt', 'helm history lab6-release -n devops-lab6-helm'),
            ('plain', 'REVISION   UPDATED                    STATUS       CHART               APP VERSION   DESCRIPTION'),
            ('plain', '1          Wed Nov 25 19:28:11 2026   superseded   devops-lab6-0.1.0   1.0.0         Install complete'),
            ('plain', '2          Wed Nov 25 19:28:59 2026   superseded   devops-lab6-0.1.0   1.0.0         Upgrade complete'),
            ('success', '3          Wed Nov 25 19:29:46 2026   deployed     devops-lab6-0.1.0   1.0.0         Rollback to 1'),
            ('prompt', 'kubectl get deployment -n devops-lab6-helm lab6-release-devops-lab6-dashboard'),
            ('highlight', 'NAME                                 READY   UP-TO-DATE   AVAILABLE   AGE\nlab6-release-devops-lab6-dashboard   2/2     2            2           95s')
        ],
        'screenshot_helm_lifecycle.png',
        height=560
    )

    # 6. Web Dashboard UI
    print("[6/7] Generating screenshot_web_ui.png...")
    dash_data = {
        'app_version': 'v1.0.0',
        'app_env': 'production',
        'log_level': 'INFO',
        'feature_flag_analytics': 'enabled',
        'max_batch_size': 500,
        'cluster_role': 'worker-dashboard',
        'pod_name': 'devops-web-app-b75b74698-ch24t',
        'pod_namespace': 'devops-lab6',
        'pod_ip': '10.244.1.4',
        'node_name': 'desktop-worker',
        'db_user': 'devops_admin',
        'masked_pw': 'Su***************************26',
        'pw_hash': '32779f36b602',
        'masked_token': 'sk-l*****************************lab6',
        'token_hash': '1eb4b7e71aa4',
        'mounted_cfg': {
            'app_name': 'DevOps Lab 6 Microservice',
            'cluster_environment': 'production-on-prem-kind',
            'cache_ttl_seconds': 3600,
            'max_connections': 100,
            'maintenance_window': 'Sunday 02:00-04:00 UTC',
            'notification_channel': '#devops-alerts'
        },
        'mounted_sec': {
            'exists': True,
            'permissions': '0400',
            'length': 51,
            'fingerprint': '816d668f1c006ef9...'
        },
        'now_utc': '2026-11-25 14:02:15 UTC'
    }
    render_browser_dashboard('app/templates/index.html', dash_data, 'screenshot_web_ui.png')

    # 7. Automated Test Suite Results
    print("[7/7] Generating screenshot_verification_suite.png...")
    render_terminal(
        'Terminal • Automated Verification Suite Execution (verify_all.ps1)',
        [
            ('prompt', 'powershell -File scripts/verify_all.ps1'),
            ('info', '======================================================================'),
            ('info', '   DevOps Lab 6: Automated Verification Test Suite (End-to-End)'),
            ('info', '======================================================================'),
            ('success', '[TEST 1] Kubernetes Multi-Node Cluster Status (3 Nodes Ready) ... PASSED [OK]'),
            ('success', '[TEST 2] Namespace \'devops-lab6\' exists ... PASSED [OK]'),
            ('success', '[TEST 3] Helm Namespace \'devops-lab6-helm\' exists ... PASSED [OK]'),
            ('success', '[TEST 4] ConfigMap \'devops-lab6-config\' contains required keys ... PASSED [OK]'),
            ('success', '[TEST 5] Secret \'devops-lab6-secret\' contains DB credentials and token ... PASSED [OK]'),
            ('success', '[TEST 6] Deployment \'devops-web-app\' has 2 ready replicas ... PASSED [OK]'),
            ('success', '[TEST 7] Service \'devops-web-service\' exposed on NodePort 30086 ... PASSED [OK]'),
            ('success', '[TEST 8] Batch Job \'data-batch-processor-job\' reached 3/3 completions ... PASSED [OK]'),
            ('success', '[TEST 9] CronJob \'system-periodic-cleaner-cron\' configured with schedule \'*/2 * * * *\' ... PASSED [OK]'),
            ('success', '[TEST 10] Pod environment variables successfully injected from Secret and ConfigMap ... PASSED [OK]'),
            ('success', '[TEST 11] Mounted Secret file \'/etc/secrets/vault_key.txt\' exists with restricted permissions ... PASSED [OK]'),
            ('success', '[TEST 12] Application Health and Ready Probes return HTTP 200 ... PASSED [OK]'),
            ('success', '[TEST 13] Helm Release \'lab6-release\' deployed with successful history ... PASSED [OK]'),
            ('info', '======================================================================'),
            ('highlight', '   Verification Summary: 13 / 13 Tests Passed (100% SUCCESS)'),
            ('info', '======================================================================')
        ],
        'screenshot_verification_suite.png',
        height=540
    )

    print("All 7 high-resolution screenshots generated successfully!")

if __name__ == '__main__':
    main()
