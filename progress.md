# Lab 6: Progress Log

## Session Details
- **Date**: 2026-11-25
- **Working Directory**: `D:\Christ\5th_Trimester\DevOps\Labs\Lab6`
- **Namespace**: `devops-lab6`

## Chronological Progress Log
- **19:08**: Inspected workspace and discovered reference repository `krypton-arch/Lab5_Kubernetes` in `../Lab5`.
- **19:10**: Started Docker Desktop daemon on Windows host and verified WSL2 backend.
- **19:11**: Downloaded and installed official Helm binary `v3.17.0` to `D:\Docker\Program\resources\bin\helm.exe`.
- **19:12**: Verified 3-node cluster connectivity (`desktop-control-plane`, `desktop-worker`, `desktop-worker2`) and Python dependencies (`python-docx`, `playwright`).
- **19:13**: Created Manus-style tracking documentation: `task_plan.md`, `findings.md`, `progress.md`.
- **19:16**: Implemented multi-mode Python application `app/app.py` supporting Web Dashboard, CLI Batch Job (`--mode=job`), and CLI CronJob (`--mode=cron`), with glassmorphism UI in `app/templates/index.html`. Built container image `lab6-microservice:v1.0.0` and imported into all 3 cluster nodes via `ctr`.
- **19:22**: Authored pure declarative Kubernetes manifests (`k8s/00-namespace.yaml` to `06-cronjob-periodic-cleaner.yaml`).
- **19:24**: Engineered enterprise Helm 3 chart in `helm/devops-lab6/` with parameterization, template helpers, NOTES.txt, and passed `helm lint` and `helm template`.
- **19:27**: Deployed base stack to namespace `devops-lab6`. Verified ConfigMap & Secret injection into running pods. Executed batch Job `data-batch-processor-job` (3/3 completions in 22s across parallel pods). Executed CronJob `system-periodic-cleaner-cron` with `Forbid` concurrency.
- **19:30**: Executed Helm 3 lifecycle: packaged chart `devops-lab6-0.1.0.tgz`, deployed release `lab6-release` (Rev 1), performed atomic upgrade to 4 replicas with `LOG_LEVEL=DEBUG` (Rev 2), and executed rollback back to Rev 1 (Rev 3: Rollback to 1).
- **19:31**: Developed PowerShell automation scripts (`deploy_raw_k8s.ps1`, `run_jobs.ps1`, `helm_lifecycle.ps1`, `verify_all.ps1`, `cleanup.ps1`). Executed `verify_all.ps1` with 13/13 tests passing (100% SUCCESS).
- **20:03**: Generated all 7 high-resolution screenshots via Playwright (`screenshot_*.png`).
- **20:06**: Compiled professional academic Word report `Lab6_Kubernetes_Jobs_Config_Helm_Report.docx` and comprehensive `README.md` lab manual adhering to CHRIST University specifications.
- **Status**: ALL 9 PHASES COMPLETE (100% SUCCESS).
