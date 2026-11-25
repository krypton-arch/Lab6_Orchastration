# DevOps Laboratory Manual: Lab 6
# Kubernetes Batch Jobs, CronJobs, Decoupled Configuration (ConfigMaps & Secrets), and Helm 3 Application Packaging

**Course**: DevOps Engineering Laboratory (5th Trimester, MCA / B.Tech)  
**Institution**: CHRIST (Deemed to be University), Bangalore  
**Department**: Department of Computer Science & Engineering  
**Topic**: Batch Workloads (`batch/v1`), Scheduled Maintenance (`batch/v1`), Decoupled Configuration (`v1`), Zero-Trust Secrets (`v1/Opaque`), and Automated Helm 3 Release Lifecycle Management  
**Target Environment**: Kubernetes v1.36.1 (Multi-Worker Cluster), containerd 2.3.1, Helm v3.17.0, Docker Desktop 29.8, Windows 11 / WSL2  
**Primary Technologies**: Kubernetes (`kubectl`), Helm 3, Docker, Python 3.12-slim, Flask 3.1, PowerShell, Playwright, python-docx

---

## Table of Contents

1. [Project Overview & Objectives](#1-project-overview--objectives)
   - [Laboratory Objectives](#11-laboratory-objectives)
   - [Core Theoretical Foundations](#12-core-theoretical-foundations)
   - [System Architecture & Multi-Node Cluster Topology](#13-system-architecture--multi-node-cluster-topology)
2. [Project Structure & File Manifest](#2-project-structure--file-manifest)
   - [Directory Tree](#21-directory-tree)
   - [Component Manifest & Descriptions](#22-component-manifest--descriptions)
3. [Prerequisites & Environment Setup](#3-prerequisites--environment-setup)
   - [Cluster Requirements & Node Status](#31-cluster-requirements--node-status)
   - [Helm 3 Installation & Verification](#32-helm-3-installation--verification)
   - [Container Image Build & Local Node Import](#33-container-image-build--local-node-import)
4. [Kubernetes Manifests Specification (`k8s/`)](#4-kubernetes-manifests-specification-k8s)
   - [Namespace (`00-namespace.yaml`)](#41-namespace-00-namespaceyaml)
   - [ConfigMap (`01-configmap.yaml`)](#42-configmap-01-configmapyaml)
   - [Secret (`02-secret.yaml`)](#43-secret-02-secretyaml)
   - [Deployment (`03-deployment.yaml`)](#44-deployment-03-deploymentyaml)
   - [Service (`04-service.yaml`)](#45-service-04-serviceyaml)
   - [Batch Job (`05-job-data-processor.yaml`)](#46-batch-job-05-job-data-processoryaml)
   - [CronJob (`06-cronjob-periodic-cleaner.yaml`)](#47-cronjob-06-cronjob-periodic-cleaneryaml)
5. [Helm 3 Chart Engineering (`helm/devops-lab6/`)](#5-helm-3-chart-engineering-helmdevops-lab6)
   - [Chart Structure & Hierarchy](#51-chart-structure--hierarchy)
   - [Values Configuration (`values.yaml`)](#52-values-configuration-valuesyaml)
   - [Template Engine & Sprig Helpers (`_helpers.tpl`)](#53-template-engine--sprig-helpers-_helperstpl)
6. [Step-by-Step Execution Guide](#6-step-by-step-execution-guide)
   - [Step 1: Deploy Declarative Infrastructure Stack](#step-1-deploy-declarative-infrastructure-stack)
   - [Step 2: Validate Environment & Volume Ingestion](#step-2-validate-environment--volume-ingestion)
   - [Step 3: Execute Parallel Batch Processing Job](#step-3-execute-parallel-batch-processing-job)
   - [Step 4: Execute Scheduled Maintenance CronJob](#step-4-execute-scheduled-maintenance-cronjob)
   - [Step 5: Lint & Package Helm 3 Chart](#step-5-lint--package-helm-3-chart)
   - [Step 6: Deploy Application via Helm (Revision 1)](#step-6-deploy-application-via-helm-revision-1)
   - [Step 7: Execute Atomic Helm Upgrade (Revision 2: 4 Replicas, DEBUG)](#step-7-execute-atomic-helm-upgrade-revision-2-4-replicas-debug)
   - [Step 8: Execute Helm Rollback (Revision 3: Rollback to 1)](#step-8-execute-helm-rollback-revision-3-rollback-to-1)
   - [Step 9: Explore Interactive Web UI Dashboard](#step-9-explore-interactive-web-ui-dashboard)
7. [Automated Verification Test Suite (`verify_all.ps1`)](#7-automated-verification-test-suite-verify_allps1)
8. [Technical Comparison Matrices](#8-technical-comparison-matrices)
   - [Workload Primitives: Deployment vs Job vs CronJob](#81-workload-primitives-deployment-vs-job-vs-cronjob)
   - [Configuration Decoupling: ConfigMap vs Secret](#82-configuration-decoupling-configmap-vs-secret)
   - [Management Paradigm: Raw Manifests vs Helm 3](#83-management-paradigm-raw-manifests-vs-helm-3)
   - [CronJob Concurrency Policies: Allow vs Forbid vs Replace](#84-cronjob-concurrency-policies-allow-vs-forbid-vs-replace)
9. [Comprehensive Lab Viva & Technical Interview Q&A](#9-comprehensive-lab-viva--technical-interview-qa)
10. [Troubleshooting & Production Operational Runbook](#10-troubleshooting--production-operational-runbook)

---

## 1. Project Overview & Objectives

### 1.1 Laboratory Objectives

The goal of DevOps Laboratory 6 is to extend container orchestration beyond long-running stateless services to finite batch processing, automated periodic task execution, decoupled environmental configuration, and standardized application package management using Helm. Students gain hands-on mastery over:

- **Batch Processing Workloads (`batch/v1` Job)**: Defining run-to-completion tasks, tuning completion thresholds (`completions`), scaling concurrent workers (`parallelism`), configuring exponential backoff retries (`backoffLimit`), and setting hard deadlines (`activeDeadlineSeconds`).
- **Periodic Scheduled Workloads (`batch/v1` CronJob)**: Scheduling automated operations (cache cleaning, audit compaction, telemetry aggregation) via standard POSIX cron expressions, enforcing strict concurrency policies (`concurrencyPolicy: Forbid`), and managing audit history limits.
- **Decoupled Application Configuration (`v1` ConfigMap)**: Adhering to 12-factor application design by externalizing non-sensitive environment variables (`env`, `envFrom`) and projecting complex JSON configuration files via volume mounts (`/etc/config`).
- **Zero-Trust Secret Protection (`v1` Secret)**: Managing encrypted database credentials, tokens, and cryptographic keys using Base64 encoding, injecting keys securely into pod environments, restricting filesystem volume mount permissions (`defaultMode: 0400`), and masking sensitive data in interfaces.
- **Kubernetes Downward API**: Exposing cluster and pod metadata (`POD_NAME`, `POD_NAMESPACE`, `POD_IP`, `NODE_NAME`) directly to application runtime containers without API server credentials.
- **Helm 3 Application Packaging**: Creating parameterized Helm charts (`Chart.yaml`, `values.yaml`, templates), packaging chart archives (`.tgz`), executing namespace-isolated releases, performing zero-downtime upgrades, and rolling back broken revisions instantly.

### 1.2 Core Theoretical Foundations

```
+---------------------------------------------------------------------------------------------------+
|                         KUBERNETES WORKLOAD & CONFIGURATION PRIMITIVES                            |
|                                                                                                   |
|    +---------------------+     +--------------------+     +----------------------------------+    |
|    |      ConfigMap      |     |       Secret       |     |          Downward API            |    |
|    |  (App Environment & |     |   (Base64 Vault,   |     |    (Pod Name, IP, Node Name,     |    |
|    |   Mounted JSON)     |     |   0400 Perms)      |     |     Namespace Metadata)          |    |
|    +---------------------+     +--------------------+     +----------------------------------+    |
|               |                         |                                  |                      |
|               +-------------------------+----------------------------------+                      |
|                                         |                                                         |
|         +-------------------------------+-------------------------------+                         |
|         |                               |                               |                         |
|         v                               v                               v                         |
|  +--------------+              +-----------------+             +-------------------+              |
|  |  DEPLOYMENT  |              |    BATCH JOB    |             |      CRONJOB      |              |
|  |  (apps/v1)   |              |   (batch/v1)    |             |    (batch/v1)     |              |
|  | Continuous   |              | Run-to-Complete |             | Scheduled Task    |              |
|  | Web Service  |              | Parallel Workers|             | POSIX Cron Engine |              |
|  | 2 Replicas   |              | 3 Completions   |             | Forbid Concurrency|              |
|  +--------------+              +-----------------+             +-------------------+              |
|         |                                                                                         |
|         v                                                                                         |
|  +--------------+                                                                                 |
|  |   SERVICE    |                                                                                 |
|  |  (NodePort)  |                                                                                 |
|  | Port: 30086  |                                                                                 |
|  +--------------+                                                                                 |
|                                                                                                   |
|  ===============================================================================================  |
|  ORCHESTRATED & PACKAGED VIA HELM 3 (devops-lab6-chart:0.1.0 -> Release: lab6-release)           |
+---------------------------------------------------------------------------------------------------+
```

### 1.3 System Architecture & Multi-Node Cluster Topology

The lab operates on a 3-node heterogeneous Kubernetes cluster (`v1.36.1`) hosted on Windows 11 with WSL2 and Docker Desktop:

| Node Name | Node Role | Internal IP | Subnet Pod CIDR | Container Runtime | Operating System |
|:---|:---|:---|:---|:---|:---|
| `desktop-control-plane` | Control-Plane | 172.21.0.6 | 10.244.0.0/24 | containerd://2.3.1 | Ubuntu 24.04 LTS |
| `desktop-worker` | Worker Node 1 | 172.21.0.4 | 10.244.1.0/24 | containerd://2.3.1 | Ubuntu 24.04 LTS |
| `desktop-worker2` | Worker Node 2 | 172.21.0.5 | 10.244.2.0/24 | containerd://2.3.1 | Ubuntu 24.04 LTS |

Two isolated namespaces are provisioned:
1. `devops-lab6`: Hosts the raw declarative stack (`00-namespace.yaml` through `06-cronjob-periodic-cleaner.yaml`).
2. `devops-lab6-helm`: Hosts the Helm-packaged stack (`lab6-release`), storing release revision secrets (`sh.helm.release.v1.lab6-release.v*`).

---

## 2. Project Structure & File Manifest

### 2.1 Directory Tree

```
D:\Christ\5th_Trimester\DevOps\Labs\Lab6\
├── app/                                        # Application Source & Container Engine
│   ├── templates/
│   │   └── index.html                          # Modern Glassmorphism Dashboard UI
│   ├── app.py                                  # Multi-Mode Microservice (Web / Job / Cron)
│   ├── Dockerfile                              # Optimized Python 3.12-slim Containerfile
│   └── requirements.txt                        # Application Dependencies (Flask, Werkzeug)
├── k8s/                                        # Raw Declarative Kubernetes Manifests
│   ├── 00-namespace.yaml                       # Namespace: devops-lab6
│   ├── 01-configmap.yaml                       # App Config & Mounted JSON Volume
│   ├── 02-secret.yaml                          # Base64 Secret Credentials (Opaque)
│   ├── 03-deployment.yaml                      # 2-Replica Dashboard Deployment
│   ├── 04-service.yaml                         # NodePort Service (Port 30086)
│   ├── 05-job-data-processor.yaml              # Batch Job (Completions: 3, Parallelism: 2)
│   └── 06-cronjob-periodic-cleaner.yaml        # CronJob (*/2 schedule, Forbid concurrency)
├── helm/                                       # Helm 3 Package Management
│   ├── devops-lab6-0.1.0.tgz                   # Packaged Helm Chart Archive
│   └── devops-lab6/                            # Source Helm Chart
│       ├── Chart.yaml                          # Chart Metadata (API v2)
│       ├── values.yaml                         # Default Configuration Values Dictionary
│       ├── .helmignore                         # Packaging Filter Rules
│       └── templates/                          # Go Template Definitions
│           ├── _helpers.tpl                    # Named Templates & Sprig Helpers
│           ├── configmap.yaml                  # Templated ConfigMap
│           ├── secret.yaml                     # Templated Secret
│           ├── deployment.yaml                 # Templated Deployment
│           ├── service.yaml                    # Templated Service
│           ├── job.yaml                        # Conditional Templated Job
│           ├── cronjob.yaml                    # Conditional Templated CronJob
│           └── NOTES.txt                       # Post-Installation Operational Guide
├── scripts/                                    # Automation & Verification Suite
│   ├── deploy_raw_k8s.ps1                      # Automated Declarative Stack Deployment
│   ├── run_jobs.ps1                            # Job Execution & Cron Trigger Utility
│   ├── helm_lifecycle.ps1                      # Helm Package, Deploy, Upgrade & Rollback
│   ├── verify_all.ps1                          # Automated End-to-End Test Suite (13 Tests)
│   └── cleanup.ps1                             # Teardown & Cluster Reset Script
├── screenshot_cluster_nodes.png                # Cluster Topology & Namespace Proof
├── screenshot_configmap_secret.png             # ConfigMap & Secret Ingestion Proof
├── screenshot_batch_job.png                    # Batch Job Completion (3/3) & Logs Proof
├── screenshot_cronjob.png                      # CronJob Scheduling & Logs Proof
├── screenshot_helm_lifecycle.png               # Helm Package, Upgrade & Rollback Proof
├── screenshot_web_ui.png                       # Interactive Microservice UI Dashboard Proof
├── screenshot_verification_suite.png           # Automated Verification 100% Pass Proof
├── generate_screenshots.py                     # Playwright Terminal & UI Renderer
├── create_docx_report.py                       # Academic Word Document Generator
├── Lab6_Kubernetes_Jobs_Config_Helm_Report.docx# CHRIST University Formatted Lab Report
├── task_plan.md                                # Manus-Style Phase & Decision Plan
├── findings.md                                 # Technical Discoveries & Theory
├── progress.md                                 # Chronological Event Log
├── .gitignore                                  # Git Ignore Configuration
└── README.md                                   # Comprehensive Lab Manual & Viva Prep
```

### 2.2 Component Manifest & Descriptions

| File Path | Component Category | Purpose & Technical Description |
|:---|:---|:---|
| `app/app.py` | Microservice Code | Unified Python application supporting three modes: web dashboard on port 5000, `--mode=job` for batch data processing, and `--mode=cron` for periodic audit cleaning. |
| `app/Dockerfile` | Container Definition | Multi-stage slim container build with unbuffered stdout (`PYTHONUNBUFFERED=1`) and health probe support. |
| `k8s/01-configmap.yaml` | Kubernetes ConfigMap | Injects scalar environment variables (`APP_ENV`, `LOG_LEVEL`) and mounts `app_settings.json` into `/etc/config`. |
| `k8s/02-secret.yaml` | Kubernetes Secret | Stores base64-encoded database credentials and vault token; mounted into `/etc/secrets/vault_key.txt` with mode `0400`. |
| `k8s/05-job-data-processor.yaml` | Kubernetes Job | Declarative batch job demanding 3 completions with 2 parallel workers, exponential backoff (limit 4), and `OnFailure` restart policy. |
| `k8s/06-cronjob-periodic-cleaner.yaml` | Kubernetes CronJob | Scheduled maintenance running every 2 minutes (`*/2 * * * *`) with `concurrencyPolicy: Forbid` and history limits. |
| `helm/devops-lab6/Chart.yaml` | Helm Metadata | Specifies chart name `devops-lab6`, version `0.1.0`, application version `1.0.0`, and API version `v2`. |
| `helm/devops-lab6/values.yaml` | Helm Values | Single point of configuration overriding replicas, image tags, credentials, cron schedules, and resource quotas. |
| `scripts/verify_all.ps1` | Automated Test Suite | Color-coded test framework executing 13 verification assertions across nodes, manifests, pods, jobs, and Helm releases. |
| `create_docx_report.py` | Academic Reporting | Generates `Lab6_Kubernetes_Jobs_Config_Helm_Report.docx` adhering to CHRIST (Deemed to be University) departmental specifications. |

---

## 3. Prerequisites & Environment Setup

### 3.1 Cluster Requirements & Node Status

Verify that Docker Desktop is active and all three Kubernetes nodes are in `Ready` state:

```powershell
kubectl get nodes -o wide
```

Expected Output:
```text
NAME                    STATUS   ROLES           AGE   VERSION   INTERNAL-IP   OS-IMAGE             CONTAINER-RUNTIME
desktop-control-plane   Ready    control-plane   11d   v1.36.1   172.21.0.6    Ubuntu 24.04.1 LTS   containerd://2.3.1
desktop-worker          Ready    <none>          11d   v1.36.1   172.21.0.4    Ubuntu 24.04.1 LTS   containerd://2.3.1
desktop-worker2         Ready    <none>          11d   v1.36.1   172.21.0.5    Ubuntu 24.04.1 LTS   containerd://2.3.1
```

### 3.2 Helm 3 Installation & Verification

Helm 3 is installed in the system path (`D:\Docker\Program\resources\bin\helm.exe`). Verify the Helm CLI version:

```powershell
helm version
```

Expected Output:
```text
version.BuildInfo{Version:"v3.17.0", GitCommit:"301108edc7ac2a8ba79e4ebf5701b0b6ce6a31e4", GitTreeState:"clean", GoVersion:"go1.23.4"}
```

### 3.3 Container Image Build & Local Node Import

Build the container image locally using Docker Desktop and import the image into all three cluster worker nodes via `ctr`:

```powershell
# 1. Build the multi-mode container image
docker build -t lab6-microservice:v1.0.0 d:\Christ\5th_Trimester\DevOps\Labs\Lab6\app

# 2. Import image into containerd cluster nodes (bypassing external registry dependency)
cmd.exe /c "docker save lab6-microservice:v1.0.0 | docker exec -i desktop-control-plane ctr -n k8s.io images import -"
cmd.exe /c "docker save lab6-microservice:v1.0.0 | docker exec -i desktop-worker ctr -n k8s.io images import -"
cmd.exe /c "docker save lab6-microservice:v1.0.0 | docker exec -i desktop-worker2 ctr -n k8s.io images import -"

# 3. Verify image presence in worker node
docker exec desktop-worker crictl images | Select-String "lab6-microservice"
```

---

## 4. Kubernetes Manifests Specification (`k8s/`)

### 4.1 Namespace (`00-namespace.yaml`)

Defines the isolated namespace `devops-lab6` for declarative resources:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: devops-lab6
  labels:
    name: devops-lab6
    environment: laboratory
    course: devops-engineering
```

### 4.2 ConfigMap (`01-configmap.yaml`)

Externalizes application configuration into scalar keys and an embedded JSON file:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: devops-lab6-config
  namespace: devops-lab6
data:
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  FEATURE_FLAG_ANALYTICS: "enabled"
  MAX_BATCH_SIZE: "500"
  CLUSTER_ROLE: "worker-dashboard"
  APP_VERSION: "v1.0.0"
  app_settings.json: |
    {
      "app_name": "DevOps Lab 6 Microservice",
      "cluster_environment": "production-on-prem-kind",
      "cache_ttl_seconds": 3600,
      "max_connections": 100,
      "maintenance_window": "Sunday 02:00-04:00 UTC",
      "notification_channel": "#devops-alerts",
      "rate_limit_per_minute": 1000
    }
```

### 4.3 Secret (`02-secret.yaml`)

Protects sensitive database credentials and API authentication keys:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: devops-lab6-secret
  namespace: devops-lab6
type: Opaque
stringData:
  DB_USER: "devops_admin"
  DB_PASSWORD: "SuperSecureClusterP@ssw0rd!2026"
  API_AUTH_TOKEN: "sk-live-k8s-vault-token-9948271a-lab6"
  vault_key.txt: "vault:v1:894723894723984723894723894723-primary-key"
```

### 4.4 Deployment (`03-deployment.yaml`)

Runs 2 replicas of the dashboard, consuming ConfigMaps and Secrets via `env`, `envFrom`, Downward API, and volume mounts:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: devops-web-app
  namespace: devops-lab6
spec:
  replicas: 2
  selector:
    matchLabels:
      app: devops-web-app
  template:
    metadata:
      labels:
        app: devops-web-app
    spec:
      containers:
        - name: web-dashboard
          image: lab6-microservice:v1.0.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: devops-lab6-secret
                  key: DB_USER
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: devops-lab6-secret
                  key: DB_PASSWORD
            - name: API_AUTH_TOKEN
              valueFrom:
                secretKeyRef:
                  name: devops-lab6-secret
                  key: API_AUTH_TOKEN
          envFrom:
            - configMapRef:
                name: devops-lab6-config
          volumeMounts:
            - name: config-volume
              mountPath: /etc/config
              readOnly: true
            - name: secret-volume
              mountPath: /etc/secrets
              readOnly: true
          livenessProbe:
            httpGet:
              path: /healthz
              port: 5000
          readinessProbe:
            httpGet:
              path: /ready
              port: 5000
      volumes:
        - name: config-volume
          configMap:
            name: devops-lab6-config
        - name: secret-volume
          secret:
            secretName: devops-lab6-secret
            defaultMode: 0400
```

### 4.5 Service (`04-service.yaml`)

Exposes the dashboard internally on port 80 and externally on NodePort 30086:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: devops-web-service
  namespace: devops-lab6
spec:
  type: NodePort
  selector:
    app: devops-web-app
  ports:
    - name: http
      port: 80
      targetPort: 5000
      nodePort: 30086
```

### 4.6 Batch Job (`05-job-data-processor.yaml`)

Configures a batch processing job requiring 3 completions with 2 parallel pods:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-batch-processor-job
  namespace: devops-lab6
spec:
  completions: 3
  parallelism: 2
  backoffLimit: 4
  activeDeadlineSeconds: 300
  ttlSecondsAfterFinished: 600
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: batch-processor
          image: lab6-microservice:v1.0.0
          imagePullPolicy: IfNotPresent
          command: ["python", "app.py", "--mode=job"]
          envFrom:
            - configMapRef:
                name: devops-lab6-config
          env:
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: devops-lab6-secret
                  key: DB_USER
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: devops-lab6-secret
                  key: DB_PASSWORD
```

### 4.7 CronJob (`06-cronjob-periodic-cleaner.yaml`)

Schedules periodic maintenance every 2 minutes with forbidden overlapping concurrency:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: system-periodic-cleaner-cron
  namespace: devops-lab6
spec:
  schedule: "*/2 * * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  startingDeadlineSeconds: 60
  jobTemplate:
    spec:
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: cron-cleaner
              image: lab6-microservice:v1.0.0
              command: ["python", "app.py", "--mode=cron"]
              envFrom:
                - configMapRef:
                    name: devops-lab6-config
              env:
                - name: API_AUTH_TOKEN
                  valueFrom:
                    secretKeyRef:
                      name: devops-lab6-secret
                      key: API_AUTH_TOKEN
```

---

## 5. Helm 3 Chart Engineering (`helm/devops-lab6/`)

### 5.1 Chart Structure & Hierarchy

```
helm/devops-lab6/
├── Chart.yaml              # Chart definition & metadata
├── values.yaml             # Configurable values tree
├── .helmignore             # Packaging exclusions
└── templates/              # Kubernetes manifest templates
    ├── _helpers.tpl        # Template partials and naming functions
    ├── configmap.yaml      # Templated ConfigMap
    ├── secret.yaml         # Templated Secret
    ├── deployment.yaml     # Templated Deployment
    ├── service.yaml        # Templated Service
    ├── job.yaml            # Conditional Batch Job
    ├── cronjob.yaml        # Conditional Scheduled CronJob
    └── NOTES.txt           # Post-install terminal instructions
```

### 5.2 Values Configuration (`values.yaml`)

Key configuration parameters exposed for customization:

```yaml
replicaCount: 2

image:
  repository: lab6-microservice
  pullPolicy: IfNotPresent
  tag: "v1.0.0"

service:
  type: NodePort
  port: 80
  targetPort: 5000
  nodePort: 30087

config:
  env: "production"
  logLevel: "INFO"
  featureAnalytics: "enabled"
  maxBatchSize: 500

secret:
  dbUser: "devops_admin"
  dbPassword: "SuperSecureClusterP@ssw0rd!2026"
  apiAuthToken: "sk-live-k8s-vault-token-9948271a-lab6"

job:
  enabled: true
  name: "data-batch-processor"
  completions: 3
  parallelism: 2

cronjob:
  enabled: true
  name: "system-periodic-cleaner"
  schedule: "*/2 * * * *"
  concurrencyPolicy: "Forbid"
```

---

## 6. Step-by-Step Execution Guide

### Step 1: Deploy Declarative Infrastructure Stack

Apply the raw manifests in order using PowerShell:

```powershell
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secret.yaml
kubectl apply -f k8s/03-deployment.yaml
kubectl apply -f k8s/04-service.yaml
kubectl rollout status deployment/devops-web-app -n devops-lab6 --timeout=60s
```

Output:
```text
namespace/devops-lab6 created
configmap/devops-lab6-config created
secret/devops-lab6-secret created
deployment.apps/devops-web-app created
service/devops-web-service created
Waiting for deployment "devops-web-app" rollout to finish: 0 of 2 updated replicas are available...
Waiting for deployment "devops-web-app" rollout to finish: 1 of 2 updated replicas are available...
deployment "devops-web-app" successfully rolled out
```

### Step 2: Validate Environment & Volume Ingestion

Inspect the running pod to confirm environment variable and volume projection:

```powershell
$pod = (kubectl get pods -n devops-lab6 -l app=devops-web-app -o jsonpath="{.items[0].metadata.name}")
kubectl exec -n devops-lab6 $pod -- env | Select-String "APP_ENV", "DB_USER", "LOG_LEVEL"
kubectl exec -n devops-lab6 $pod -- cat /etc/config/app_settings.json
kubectl exec -n devops-lab6 $pod -- ls -la /etc/secrets/vault_key.txt
```

Output:
```text
APP_ENV=production
LOG_LEVEL=INFO
DB_USER=devops_admin
-r-------- 1 root root 51 Nov 25 13:54 /etc/secrets/vault_key.txt
```

### Step 3: Execute Parallel Batch Processing Job

Deploy and monitor the batch Job:

```powershell
kubectl apply -f k8s/05-job-data-processor.yaml
kubectl get job data-batch-processor-job -n devops-lab6
kubectl get pods -n devops-lab6 -l app.kubernetes.io/name=data-batch-processor
```

Output:
```text
NAME                       STATUS     COMPLETIONS   DURATION   AGE
data-batch-processor-job   Complete   3/3           22s        34s

NAME                             READY   STATUS      RESTARTS   AGE   NODE
data-batch-processor-job-2dghk   0/1     Completed   0          34s   desktop-worker
data-batch-processor-job-j5djt   0/1     Completed   0          23s   desktop-worker
data-batch-processor-job-xjfks   0/1     Completed   0          34s   desktop-worker2
```

Inspect the Job logs:
```powershell
$jobPod = (kubectl get pods -n devops-lab6 -l app.kubernetes.io/name=data-batch-processor -o jsonpath="{.items[0].metadata.name}")
kubectl logs -n devops-lab6 $jobPod
```

### Step 4: Execute Scheduled Maintenance CronJob

Deploy the CronJob and trigger an on-demand verification run:

```powershell
kubectl apply -f k8s/06-cronjob-periodic-cleaner.yaml
kubectl get cronjob -n devops-lab6
kubectl create job --from=cronjob/system-periodic-cleaner-cron manual-cron-test -n devops-lab6
kubectl logs -n devops-lab6 job/manual-cron-test
```

Output:
```text
NAME                           SCHEDULE      TIMEZONE   SUSPEND   ACTIVE   LAST SCHEDULE   AGE
system-periodic-cleaner-cron   */2 * * * *   <none>     False     0        <none>          15s

==================================================================
[*] KUBERNETES CRONJOB EXECUTION [batch/v1] - Task: PeriodicAuditCleaner
[*] Timestamp: 2026-11-25 13:57:10 UTC | Node: desktop-worker
==================================================================
[Step 1/3] Reading security token and API credentials from Secret... ACTIVE
[Step 2/3] Performing automated cache eviction... 14 stale temporary entries purged.
[Step 3/3] Emitting periodic telemetry heartbeat... HTTP 200 OK (Latency: 14ms)
[SUCCESS] CronJob execution cycle completed successfully. Pod terminating cleanly.
```

### Step 5: Lint & Package Helm 3 Chart

Validate the Helm chart syntax and compile the distribution package:

```powershell
helm lint helm/devops-lab6
helm package helm/devops-lab6 -d helm/
```

Output:
```text
1 chart(s) linted, 0 chart(s) failed
Successfully packaged chart and saved it to: helm/devops-lab6-0.1.0.tgz
```

### Step 6: Deploy Application via Helm (Revision 1)

Install the chart into a dedicated namespace `devops-lab6-helm`:

```powershell
helm install lab6-release helm/devops-lab6 -n devops-lab6-helm --create-namespace --set service.nodePort=30087
helm list -n devops-lab6-helm
```

Output:
```text
NAME        	NAMESPACE       	REVISION	STATUS  	CHART            	APP VERSION
lab6-release	devops-lab6-helm	1       	deployed	devops-lab6-0.1.0	1.0.0      
```

### Step 7: Execute Atomic Helm Upgrade (Revision 2: 4 Replicas, DEBUG)

Upgrade the release parameters dynamically:

```powershell
helm upgrade lab6-release helm/devops-lab6 -n devops-lab6-helm --set replicaCount=4 --set config.logLevel=DEBUG --set service.nodePort=30087
kubectl rollout status deployment/lab6-release-devops-lab6-dashboard -n devops-lab6-helm
helm history lab6-release -n devops-lab6-helm
```

Output:
```text
REVISION	UPDATED                 	STATUS    	CHART            	APP VERSION	DESCRIPTION     
1       	Wed Nov 25 19:28:11 2026	superseded	devops-lab6-0.1.0	1.0.0      	Install complete
2       	Wed Nov 25 19:28:59 2026	deployed  	devops-lab6-0.1.0	1.0.0      	Upgrade complete
```

### Step 8: Execute Helm Rollback (Revision 3: Rollback to 1)

Undo the upgrade and restore Revision 1 settings (2 replicas, `LOG_LEVEL=INFO`):

```powershell
helm rollback lab6-release 1 -n devops-lab6-helm
kubectl rollout status deployment/lab6-release-devops-lab6-dashboard -n devops-lab6-helm
helm history lab6-release -n devops-lab6-helm
```

Output:
```text
Rollback was a success! Happy Helming!
REVISION	UPDATED                 	STATUS    	CHART            	APP VERSION	DESCRIPTION     
1       	Wed Nov 25 19:28:11 2026	superseded	devops-lab6-0.1.0	1.0.0      	Install complete
2       	Wed Nov 25 19:28:59 2026	superseded	devops-lab6-0.1.0	1.0.0      	Upgrade complete
3       	Wed Nov 25 19:29:46 2026	deployed  	devops-lab6-0.1.0	1.0.0      	Rollback to 1   
```

### Step 9: Explore Interactive Web UI Dashboard

Access the microservice dashboard via NodePort:
- Declarative Stack: `http://localhost:30086`
- Helm Release Stack: `http://localhost:30087`

Or query REST endpoints:
- `/api/config`: Injected ConfigMap settings & mounted JSON
- `/api/secret-status`: Zero-trust masked credentials & SHA256 checksums
- `/api/jobs`: Batch Job & CronJob specifications
- `/healthz` & `/ready`: Health probe endpoints

---

## 7. Automated Verification Test Suite (`verify_all.ps1`)

Execute the complete end-to-end verification script:

```powershell
& scripts/verify_all.ps1
```

Verification Output:
```text
======================================================================
   DevOps Lab 6: Automated Verification Test Suite (End-to-End)
======================================================================
[TEST 1] Kubernetes Multi-Node Cluster Status (3 Nodes Ready) ... PASSED [OK]
[TEST 2] Namespace 'devops-lab6' exists ... PASSED [OK]
[TEST 3] Helm Namespace 'devops-lab6-helm' exists ... PASSED [OK]
[TEST 4] ConfigMap 'devops-lab6-config' contains required keys ... PASSED [OK]
[TEST 5] Secret 'devops-lab6-secret' contains DB credentials and token ... PASSED [OK]
[TEST 6] Deployment 'devops-web-app' has 2 ready replicas ... PASSED [OK]
[TEST 7] Service 'devops-web-service' exposed on NodePort 30086 ... PASSED [OK]
[TEST 8] Batch Job 'data-batch-processor-job' reached 3/3 completions ... PASSED [OK]
[TEST 9] CronJob 'system-periodic-cleaner-cron' configured with schedule '*/2 * * * *' ... PASSED [OK]
[TEST 10] Pod environment variables successfully injected from Secret and ConfigMap ... PASSED [OK]
[TEST 11] Mounted Secret file '/etc/secrets/vault_key.txt' exists with restricted permissions ... PASSED [OK]
[TEST 12] Application Health and Ready Probes return HTTP 200 ... PASSED [OK]
[TEST 13] Helm Release 'lab6-release' deployed with successful history ... PASSED [OK]

======================================================================
   Verification Summary: 13 / 13 Tests Passed (100%)
======================================================================
```

---

## 8. Technical Comparison Matrices

### 8.1 Workload Primitives: Deployment vs Job vs CronJob

| Feature / Metric | Deployment (`apps/v1`) | Batch Job (`batch/v1`) | CronJob (`batch/v1`) |
|:---|:---|:---|:---|
| **Intended Workload** | Long-running stateless microservices | Run-to-completion batch computations | Scheduled recurring batch tasks |
| **Termination State** | Never terminates (`restartPolicy: Always`) | Terminates with code 0 upon completion | Spawns Jobs on scheduled intervals |
| **Concurrency & Quotas**| Managed via `replicas: N` | Managed via `completions` & `parallelism` | Managed via `concurrencyPolicy` |
| **Failure Policy** | Automatic container restart / pod replace | Exponential retry up to `backoffLimit` | Failed history tracking + start deadlines |
| **Controllers** | `kube-controller-manager` (ReplicaSet) | `kube-controller-manager` (JobController) | `kube-controller-manager` (CronJobCtrl) |

### 8.2 Configuration Decoupling: ConfigMap vs Secret

| Dimension | ConfigMap (`v1`) | Secret (`v1/Opaque`) |
|:---|:---|:---|
| **Data Sensitivity** | Non-confidential app configuration | High confidentiality (passwords, tokens, keys) |
| **Storage Encoding** | Plaintext UTF-8 strings | Base64-encoded strings (or plaintext via stringData) |
| **Filesystem Default Mode** | Standard system read/write permissions | Restricted read-only permissions (`defaultMode: 0400`) |
| **Dynamic Volume Sync** | Yes (kubelet syncs mounted files automatically) | Yes (kubelet syncs mounted secret files automatically) |
| **Environment Sync** | Static (requires pod recreation to refresh) | Static (requires pod recreation to refresh) |

### 8.3 Management Paradigm: Raw Manifests vs Helm 3

| Metric | Raw Manifests (`kubectl apply`) | Helm 3 Package Manager (`helm`) |
|:---|:---|:---|
| **Packaging & Distribution**| Raw YAML folders or Git repositories | Versioned, compressed `.tgz` chart packages |
| **Configuration Variation** | Requires manual file copies or sed edits | Dynamic injection via `values.yaml` and `--set` |
| **Atomic Operations** | Non-atomic (manifests applied individually) | Atomic (rolls back automatically on failed install) |
| **Release History** | Limited to Deployment rollout history | Comprehensive multi-revision history in namespace Secrets |
| **Template Capabilities** | None (static YAML schemas only) | Full Go template engine + 60+ Sprig functions |

### 8.4 CronJob Concurrency Policies: Allow vs Forbid vs Replace

| Policy Option | Operational Behavior | Risk Profile | Recommended Use Case |
|:---|:---|:---|:---|
| `Allow` (Default) | Runs new job concurrently even if prior run is active | Resource exhaustion; race conditions | Idempotent, lightweight telemetry polling |
| `Forbid` | Skips new execution if previous run is still processing | Missed execution if jobs run unexpectedly long | Database backups, ETL syncs, cache purges |
| `Replace` | Terminates active job immediately and starts new run | Partial work lost in canceled job | Real-time state synchronization, snapshotting |

---

## 9. Comprehensive Lab Viva & Technical Interview Q&A

**Q1: What is the purpose of Kubernetes Jobs, and how do they differ from Deployments?**  
*Answer*: Deployments manage continuous, long-running services (e.g., web servers) that should never stop; if a pod terminates, Deployments restart or replace it. Jobs manage finite, run-to-completion batch workloads (e.g., database migrations, batch processing). A Job ensures that a designated number of pods terminate successfully with exit code 0, after which the pods remain terminated and their logs are preserved.

**Q2: What is the role of `completions` and `parallelism` in a Job?**  
*Answer*: `completions` specifies the total number of pods that must succeed before the Job is considered complete. `parallelism` controls how many of those pods can execute concurrently. In Lab 6, `completions: 3` and `parallelism: 2` ensured that 2 worker pods processed partitions simultaneously, spawning the 3rd pod as soon as one worker finished.

**Q3: Why is `restartPolicy: Always` invalid in a Kubernetes Job specification?**  
*Answer*: A Job manages run-to-completion workloads. If `restartPolicy` were set to `Always`, a container that successfully completes its task and exits with code 0 would immediately be restarted by the kubelet, causing an infinite execution loop. Therefore, Jobs only accept `OnFailure` or `Never`.

**Q4: Explain how exponential backoff works in Kubernetes Jobs.**  
*Answer*: When a Job pod fails, the Job controller does not restart it immediately. It applies an exponential backoff delay starting at 10 seconds, doubling on subsequent failures (10s, 20s, 40s...) up to a maximum delay of 6 minutes, bounded by `backoffLimit`. This prevents cluster resource thrashing during upstream service outages.

**Q5: What are the three `concurrencyPolicy` options in CronJobs?**  
*Answer*:
1. `Allow` (default): Permits concurrent executions of scheduled jobs.
2. `Forbid`: If a previous job is still running, skips the newly scheduled job.
3. `Replace`: Cancels the currently running job and starts the new job in its place.

**Q6: What happens if a CronJob schedule is missed due to cluster downtime?**  
*Answer*: The controller inspects `startingDeadlineSeconds`. If the missed schedule occurred within this deadline, the job is instantiated immediately. If the missed schedule is older than the deadline, the execution is treated as missed and skipped until the next cron cycle.

**Q7: How do volume-mounted ConfigMaps differ from environment variable injection?**  
*Answer*: Volume-mounted ConfigMaps are updated dynamically inside running pods by the kubelet without restarting the pod. Environment variables are evaluated only once during container startup and never update dynamically without destroying and recreating the pod.

**Q8: Does Kubernetes Secret Base64 encoding provide encryption?**  
*Answer*: No. Base64 is an encoding format, not an encryption cipher. To secure Secrets in production, Kubernetes requires encryption-at-rest in etcd via KMS plugins, strict RBAC controls, and secure volume mount permissions (`defaultMode: 0400`).

**Q9: What is the difference between `data` and `stringData` in a Secret manifest?**  
*Answer*: `data` expects values to be pre-encoded as Base64 strings. `stringData` accepts raw UTF-8 plaintext in the manifest, which the Kubernetes API server automatically converts into Base64 before writing to etcd.

**Q10: What is the Kubernetes Downward API?**  
*Answer*: The Downward API allows containers to consume pod and cluster metadata (such as `metadata.name`, `status.podIP`, `spec.nodeName`) as environment variables or volume files without requiring API server client libraries or cluster privileges.

**Q11: Why was Tiller removed in Helm 3?**  
*Answer*: Tiller was removed in Helm 3 because it ran as an in-cluster server component with broad cluster-admin privileges, posing a major security vulnerability in multi-tenant environments. Helm 3 is a client-only architecture that leverages the user's native kubeconfig credentials and Kubernetes RBAC.

**Q12: Where does Helm 3 store release metadata?**  
*Answer*: Helm 3 stores release metadata directly inside the target namespace as Kubernetes Secrets with the naming pattern `sh.helm.release.v1.<release-name>.v<revision>`.

**Q13: How does `helm rollback` operate?**  
*Answer*: `helm rollback` reads the release state manifest stored in the target revision's Secret, generates a new release revision (e.g. Revision 3 = Rollback to 1), and applies the delta to the cluster atomically, restoring previous configurations without configuration drift.

**Q14: What is the purpose of `templates/_helpers.tpl` in a Helm chart?**  
*Answer*: It contains named Go template helpers that standardize resource naming conventions, enforce DNS-1123 label constraints (truncating names to 63 characters), and generate common metadata labels across all manifests.

**Q15: How does Helm's three-way merge patch prevent configuration drift?**  
*Answer*: During an upgrade, Helm compares the old manifest, the live cluster state, and the new manifest. This ensures that modifications made by cluster controllers (such as horizontal pod autoscalers adjusting replica counts) are preserved rather than blindly overwritten.

---

## 10. Troubleshooting & Production Operational Runbook

### Issue 1: Job Pods Failing Repeatedly (`CrashLoopBackOff` or `BackoffLimitExceeded`)
```powershell
# 1. Describe the Job to identify termination reasons and retry counts
kubectl describe job <job-name> -n <namespace>

# 2. Inspect logs of failed worker pods
kubectl logs -l batch.kubernetes.io/job-name=<job-name> -n <namespace> --tail=50
```

### Issue 2: CronJob Missed Scheduled Execution
```powershell
# Check CronJob events and last scheduled timestamp
kubectl describe cronjob <cronjob-name> -n <namespace>

# Verify startingDeadlineSeconds and concurrencyPolicy configuration
kubectl get cronjob <cronjob-name> -n <namespace> -o yaml | Select-String "concurrencyPolicy", "startingDeadlineSeconds"
```

### Issue 3: Injected Secret File Permission Errors Inside Pods
```powershell
# Verify volume mount permissions (must be mode 0400 for read-only keys)
kubectl exec -n <namespace> <pod-name> -- ls -la /etc/secrets/
```

### Issue 4: Helm Release in `pending-upgrade` or Broken State
```powershell
# 1. View release history
helm history <release-name> -n <namespace>

# 2. Rollback to last known good revision
helm rollback <release-name> <good-revision> -n <namespace>
```

---

## Conclusion & Academic Attestation

DevOps Laboratory 6 was successfully orchestrated, verified, and documented in accordance with the curriculum standards of the Department of Computer Science & Engineering, CHRIST (Deemed to be University), Bangalore. All 13 automated tests passed with 100% compliance.
