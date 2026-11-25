# DevOps Laboratory 6: Teardown and Cleanup Script
# CHRIST (Deemed to be University) - Department of Computer Science & Engineering

Write-Host "==========================================================" -ForegroundColor Red
Write-Host "   DevOps Lab 6: Cluster Teardown and Cleanup" -ForegroundColor Red
Write-Host "==========================================================" -ForegroundColor Red

Write-Host "`n[Step 1/3] Uninstalling Helm Release 'lab6-release'..." -ForegroundColor Yellow
helm uninstall lab6-release -n devops-lab6-helm 2>$null

Write-Host "`n[Step 2/3] Deleting Helm Namespace 'devops-lab6-helm'..." -ForegroundColor Yellow
kubectl delete namespace devops-lab6-helm 2>$null

Write-Host "`n[Step 3/3] Deleting Declarative Namespace 'devops-lab6'..." -ForegroundColor Yellow
kubectl delete namespace devops-lab6 2>$null

Write-Host "`nCleanup Complete! Cluster returned to baseline state." -ForegroundColor Green
