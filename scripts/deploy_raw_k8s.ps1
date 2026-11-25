# DevOps Laboratory 6: Raw Kubernetes Stack Deployment Script
# CHRIST (Deemed to be University) - Department of Computer Science & Engineering

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   DevOps Lab 6: Raw Kubernetes Workload Deployment" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$K8S_DIR = Join-Path $PSScriptRoot "..\k8s"

Write-Host "`n[Step 1/5] Applying Namespace (devops-lab6)..." -ForegroundColor Yellow
kubectl apply -f (Join-Path $K8S_DIR "00-namespace.yaml")

Write-Host "`n[Step 2/5] Applying ConfigMap (devops-lab6-config)..." -ForegroundColor Yellow
kubectl apply -f (Join-Path $K8S_DIR "01-configmap.yaml")

Write-Host "`n[Step 3/5] Applying Secret (devops-lab6-secret)..." -ForegroundColor Yellow
kubectl apply -f (Join-Path $K8S_DIR "02-secret.yaml")

Write-Host "`n[Step 4/5] Applying Deployment (devops-web-app)..." -ForegroundColor Yellow
kubectl apply -f (Join-Path $K8S_DIR "03-deployment.yaml")

Write-Host "`n[Step 5/5] Applying Service (NodePort 30086)..." -ForegroundColor Yellow
kubectl apply -f (Join-Path $K8S_DIR "04-service.yaml")

Write-Host "`nWaiting for Deployment rollout to complete..." -ForegroundColor Yellow
kubectl rollout status deployment/devops-web-app -n devops-lab6 --timeout=90s

Write-Host "`nDeployment Summary in Namespace 'devops-lab6':" -ForegroundColor Green
kubectl get all,configmap,secret -n devops-lab6 -o wide
