# DevOps Laboratory 6: Jobs & CronJobs Execution and Telemetry Script
# CHRIST (Deemed to be University) - Department of Computer Science & Engineering

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   DevOps Lab 6: Batch Jobs & CronJobs Execution" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$K8S_DIR = Join-Path $PSScriptRoot "..\k8s"

Write-Host "`n[Step 1/4] Applying Batch Job Manifest (completions: 3, parallelism: 2)..." -ForegroundColor Yellow
kubectl apply -f (Join-Path $K8S_DIR "05-job-data-processor.yaml")

Write-Host "`n[Step 2/4] Monitoring Batch Job Execution..." -ForegroundColor Yellow
$timeout = 60
$elapsed = 0
while ($elapsed -lt $timeout) {
    $status = kubectl get job data-batch-processor-job -n devops-lab6 -o jsonpath="{.status.succeeded}" 2>$null
    Write-Host "Current Completed Pods: $status/3 (Elapsed: ${elapsed}s)..." -ForegroundColor Gray
    if ($status -eq "3") {
        Write-Host "Job reached 3/3 completions successfully!" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 4
    $elapsed += 4
}

Write-Host "`n[Step 3/4] Batch Job Pod Execution Logs:" -ForegroundColor Yellow
$jobPod = kubectl get pods -n devops-lab6 -l app.kubernetes.io/name=data-batch-processor -o jsonpath="{.items[0].metadata.name}"
kubectl logs -n devops-lab6 $jobPod

Write-Host "`n[Step 4/4] Applying CronJob Manifest & Executing On-Demand Trigger..." -ForegroundColor Yellow
kubectl apply -f (Join-Path $K8S_DIR "06-cronjob-periodic-cleaner.yaml")
kubectl get cronjob -n devops-lab6

Write-Host "`nTriggering immediate manual run from CronJob template..." -ForegroundColor Yellow
$testJobName = "manual-cron-run-$(Get-Random -Minimum 1000 -Maximum 9999)"
kubectl create job --from=cronjob/system-periodic-cleaner-cron $testJobName -n devops-lab6
Start-Sleep -Seconds 6
kubectl logs -n devops-lab6 "job/$testJobName"
