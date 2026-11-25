# Lab 6: Kubernetes Jobs, CronJobs, ConfigMaps, Secrets, and Helm Deployment
## Task Planning & Execution Tracker

### User Request
Create Jobs and CronJobs, manage configuration using ConfigMaps and Secrets, and deploy applications using Helm.
Reference repository pattern: https://github.com/krypton-arch/Lab5_Kubernetes

### Target Environment & Tech Stack
- **OS**: Windows 11 / WSL2
- **Kubernetes Version**: v1.36.1 (Multi-Node: `desktop-control-plane`, `desktop-worker`, `desktop-worker2`)
- **Helm Version**: v3.17.0
- **Docker Engine**: 29.8.0
- **Container Runtime**: containerd 2.3.1
- **Workspace**: `D:\Christ\5th_Trimester\DevOps\Labs\Lab6`
- **Target Namespace**: `devops-lab6`
- **Primary Tech**: Kubernetes API (`batch/v1`, `v1`, `apps/v1`), Helm 3, Python 3.12/Flask, Docker, PowerShell, Playwright, python-docx

---

### Phases & Milestones

- [x] **Phase 1: Environment Discovery & Architecture Design**
  - Verified Kubernetes cluster nodes, containerd runtime, and Helm CLI integration
  - Design unified microservice architecture (Flask Web App + Dual Batch/Cron CLI processor)
  - Design ConfigMap (app settings, feature flags) & Secret (DB credentials, API token, TLS key) schemas
  - Design Job specifications (data migration / batch report with completions & parallelism)
  - Design CronJob specifications (periodic audit/backup with cron schedule & concurrencyPolicy)
  - Design enterprise-grade Helm Chart structure (`devops-lab6`)
  - Created planning and tracking documents (`task_plan.md`, `findings.md`, `progress.md`)

- [x] **Phase 2: Application Development & Container Image Build**
  - Create multi-modal application `app/app.py`:
    - Web Dashboard: renders UI showing ConfigMap params, masked Secret credentials, Job telemetry, and Pod metadata
    - REST API: endpoints `/api/config`, `/api/secret-status`, `/api/jobs`, `/healthz`, `/ready`
    - CLI Batch Job mode: executes batch operations, logs data processing milestones, exits 0 on success
    - CLI CronJob mode: periodic telemetry and cache maintenance, exits 0 on success
  - Create modern, responsive HTML/CSS dashboard template in `app/templates/index.html`
  - Create multi-stage / slim Dockerfile (`app/Dockerfile`)
  - Built local container image `lab6-microservice:v1.0.0`
  - Loaded container image into all Kind/containerd cluster nodes (`desktop-control-plane`, `desktop-worker`, `desktop-worker2`)

- [x] **Phase 3: Declarative Kubernetes Manifests (`k8s/`)**
  - `00-namespace.yaml`: Namespace definition `devops-lab6`
  - `01-configmap.yaml`: Environmental configuration & application settings
  - `02-secret.yaml`: Base64-encoded credentials (DB password, API authentication tokens)
  - `03-deployment.yaml`: Deployment consuming ConfigMaps and Secrets via env and volume mounts
  - `04-service.yaml`: ClusterIP and NodePort services for dashboard access
  - `05-job-data-processor.yaml`: Batch Job (`batch/v1`) with completions, parallelism, and backoffLimit
  - `06-cronjob-periodic-cleaner.yaml`: Periodic CronJob (`batch/v1`) with schedule, concurrencyPolicy, and history limits

- [x] **Phase 4: Helm Chart Development (`helm/devops-lab6`)**
  - Initialized clean Helm chart structure with `Chart.yaml`, `values.yaml`, `.helmignore`, `templates/`
  - Authored templates: `_helpers.tpl`, `configmap.yaml`, `secret.yaml`, `deployment.yaml`, `service.yaml`, `job.yaml`, `cronjob.yaml`, `NOTES.txt`
  - Parameterized all resource attributes (replicas, image tags, config values, secrets, cron schedule, resources)
  - Validated Helm chart syntax using `helm lint` and `helm template`

- [x] **Phase 5: Deployment, Verification & Live Execution**
  - Deployed raw Kubernetes manifests to `devops-lab6` and verified execution
  - Validated ConfigMap and Secret injection (environment variables and mounted secret files)
  - Executed and monitored batch Job execution (parallel pods, completions 3/3, logs, completion status)
  - Executed and observed CronJob scheduling (trigger manual run, observe scheduled trigger, history limits)
  - Tested Web UI and API endpoints (`/`, `/api/config`, `/api/secret-status`)

- [x] **Phase 6: Helm Lifecycle Operations**
  - Packaged Helm chart (`helm package`)
  - Installed release `lab6-release` into `devops-lab6-helm` namespace
  - Performed Helm release upgrade (`helm upgrade`) with modified values (replicaCount 4, LOG_LEVEL DEBUG)
  - Inspected release history (`helm history`)
  - Performed Helm rollback (`helm rollback`) to previous release revision 1 (2 replicas, LOG_LEVEL INFO)
  - Verified zero configuration drift and status consistency

- [x] **Phase 7: Automation Scripts Suite (`scripts/`)**
  - `deploy_raw_k8s.ps1`: Automated deployment of standalone manifests
  - `run_jobs.ps1`: Triggering and log inspection of Jobs and CronJobs
  - `helm_lifecycle.ps1`: Packaging, installing, upgrading, and rolling back via Helm
  - `verify_all.ps1`: Comprehensive automated validation test suite with color-coded test asserts (13/13 100% Passed)
  - `cleanup.ps1`: Safe teardown and cleanup utility

- [x] **Phase 8: High-Resolution Visual Evidence Generation (`generate_screenshots.py`)**
  - Created script to generate pixel-perfect terminal and Web UI screenshots using Playwright
  - Generated visual proofs:
    - `screenshot_cluster_nodes.png`: Cluster & Node Health
    - `screenshot_configmap_secret.png`: ConfigMap & Secret Verification
    - `screenshot_batch_job.png`: Batch Job Execution & Parallelism
    - `screenshot_cronjob.png`: CronJob Scheduling & History
    - `screenshot_helm_lifecycle.png`: Helm Lint, Install, Upgrade & Rollback
    - `screenshot_web_ui.png`: Application Web UI Dashboard
    - `screenshot_verification_suite.png`: Automated Verification Suite Results

- [x] **Phase 9: Comprehensive Lab Documentation & Academic Report**
  - Authored publication-grade `README.md` (comprehensive theoretical foundations, ASCII architecture diagrams, step-by-step guides, comparison matrices, 15 viva questions, operational runbook)
  - Created `create_docx_report.py` and compiled `Lab6_Kubernetes_Jobs_Config_Helm_Report.docx` (730 KB) adhering to CHRIST University departmental standards
  - Configured `.gitignore` and persistent workspace files
