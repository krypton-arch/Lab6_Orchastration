# Lab 6: Discoveries and Research Findings

## Cluster Architecture & State
- **Kubernetes Version**: v1.36.1
- **Nodes**:
  - `desktop-control-plane` (Ready, Control-Plane, 172.21.0.6)
  - `desktop-worker` (Ready, Worker Node 1, 172.21.0.4)
  - `desktop-worker2` (Ready, Worker Node 2, 172.21.0.5)
- **Container Runtime**: containerd 2.3.1
- **Helm Version**: v3.17.0 (installed at `D:\Docker\Program\resources\bin\helm.exe`)
- **Docker Engine**: 29.8.0
- **Network Plugin**: kindnet (CNI)

## Core Technical Concepts & In-Depth Insights
1. **Kubernetes Jobs (`batch/v1`)**:
   - Designed for non-continuous, run-to-completion workloads (batch processing, data ETL, schema migrations).
   - Key primitives:
     - `completions`: Specifies how many Pods must successfully terminate before the Job is marked `Complete`.
     - `parallelism`: Maximum number of Pods allowed to run concurrently.
     - `backoffLimit`: Number of retries before marking the Job failed (exponential backoff: 10s, 20s, 40s...).
     - `restartPolicy`: Must be either `OnFailure` (container restarts inside same pod) or `Never` (failed pod stays failed, new pod created).
     - `activeDeadlineSeconds`: Maximum job execution duration before termination.
     - `ttlSecondsAfterFinished`: Automatic garbage collection of completed jobs and associated pods.

2. **Kubernetes CronJobs (`batch/v1`)**:
   - Manages time-based Jobs using standard POSIX cron syntax (`minute hour day-of-month month day-of-week`).
   - Key primitives:
     - `concurrencyPolicy`:
       - `Allow` (default): Concurrent jobs can run simultaneously.
       - `Forbid`: Skips the new job if previous has not completed.
       - `Replace`: Cancels the currently running job and starts a new one.
     - `successfulJobsHistoryLimit`: Retention count for successful Job records (default: 3).
     - `failedJobsHistoryLimit`: Retention count for failed Job records (default: 1).
     - `startingDeadlineSeconds`: Deadline in seconds for starting the job if it misses scheduled time.

3. **ConfigMaps (`v1`)**:
   - Decouples configuration artifacts from container image content for 12-factor application portability.
   - Consumed via:
     - Environment variables (`valueFrom.configMapKeyRef` or `envFrom.configMapRef`).
     - Volume mounts (`spec.volumes[].configMap` -> `volumeMounts`). Updates to mounted ConfigMaps are dynamically synced by `kubelet` without pod restart!

4. **Secrets (`v1`)**:
   - Stores confidential data (passwords, tokens, keys) as base64-encoded strings (or stringData).
   - Type `Opaque` used for arbitrary user-defined key-value secrets.
   - Consumed via `secretKeyRef` or volume mounts with restricted filesystem permissions (`defaultMode: 0400` or `0440`).
   - Best practices: Avoid committing plaintext secrets to Git, mask secret values in UI and logs.

5. **Helm 3 Architecture**:
   - Client-only architecture (Tiller removed in Helm 3).
   - Communicates directly with Kubernetes API server using kubeconfig.
   - Release metadata stored directly in Kubernetes Secrets within the target namespace.
   - Three-way merge patch on upgrades (`last-applied-configuration`, current live state, new manifest).
   - Templating engine based on Go templates and Sprig library.
