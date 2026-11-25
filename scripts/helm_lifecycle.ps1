# DevOps Laboratory 6: Helm Package, Deploy, Upgrade & Rollback Automation Script
# CHRIST (Deemed to be University) - Department of Computer Science & Engineering

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   DevOps Lab 6: Helm 3 Application Lifecycle Automation" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$CHART_DIR = Join-Path $PSScriptRoot "..\helm\devops-lab6"
$OUTPUT_DIR = Join-Path $PSScriptRoot "..\helm"
$RELEASE_NAME = "lab6-release"
$NAMESPACE = "devops-lab6-helm"

Write-Host "`n[Step 1/6] Linting Helm Chart..." -ForegroundColor Yellow
helm lint $CHART_DIR

Write-Host "`n[Step 2/6] Packaging Helm Chart..." -ForegroundColor Yellow
helm package $CHART_DIR -d $OUTPUT_DIR

Write-Host "`n[Step 3/6] Installing Helm Release (Revision 1)..." -ForegroundColor Yellow
helm upgrade --install $RELEASE_NAME $CHART_DIR -n $NAMESPACE --create-namespace --set service.nodePort=30087

Write-Host "`nWaiting for Deployment rollout..." -ForegroundColor Yellow
kubectl rollout status deployment/$RELEASE_NAME-devops-lab6-dashboard -n $NAMESPACE --timeout=90s

Write-Host "`n[Step 4/6] Upgrading Helm Release (Revision 2: 4 Replicas, LOG_LEVEL=DEBUG)..." -ForegroundColor Yellow
helm upgrade $RELEASE_NAME $CHART_DIR -n $NAMESPACE --set replicaCount=4 --set config.logLevel=DEBUG --set service.nodePort=30087
kubectl rollout status deployment/$RELEASE_NAME-devops-lab6-dashboard -n $NAMESPACE --timeout=90s

Write-Host "`n[Step 5/6] Inspecting Helm Release History..." -ForegroundColor Yellow
helm history $RELEASE_NAME -n $NAMESPACE

Write-Host "`n[Step 6/6] Rolling Back Helm Release to Revision 1..." -ForegroundColor Yellow
helm rollback $RELEASE_NAME 1 -n $NAMESPACE
kubectl rollout status deployment/$RELEASE_NAME-devops-lab6-dashboard -n $NAMESPACE --timeout=90s

Write-Host "`nFinal Helm Release History & Deployment Status:" -ForegroundColor Green
helm history $RELEASE_NAME -n $NAMESPACE
kubectl get deployment -n $NAMESPACE $RELEASE_NAME-devops-lab6-dashboard
