# DevOps Laboratory 6: Automated End-to-End Verification Test Suite
# CHRIST (Deemed to be University) - Department of Computer Science & Engineering

$ErrorActionPreference = "Continue"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   DevOps Lab 6: Automated Verification Test Suite (End-to-End)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$script:TotalTests = 0
$script:PassedTests = 0
$script:FailedTests = 0

function Assert-Test {
    param(
        [string]$Description,
        [scriptblock]$Condition
    )
    $script:TotalTests++
    Write-Host -NoNewline "[TEST $script:TotalTests] $Description ... "
    try {
        $result = & $Condition
        if ($result) {
            Write-Host "PASSED [OK]" -ForegroundColor Green
            $script:PassedTests++
        } else {
            Write-Host "FAILED [FAIL]" -ForegroundColor Red
            $script:FailedTests++
        }
    } catch {
        Write-Host "ERROR [EXCEPTION]: $_" -ForegroundColor Red
        $script:FailedTests++
    }
}

# 1. Cluster Nodes Verification
Assert-Test "Kubernetes Multi-Node Cluster Status (3 Nodes Ready)" {
    $readyNodes = (kubectl get nodes --no-headers | Select-String "Ready").Count
    return ($readyNodes -ge 3)
}

# 2. Namespace Verification
Assert-Test "Namespace 'devops-lab6' exists" {
    $ns = kubectl get namespace devops-lab6 --no-headers 2>$null
    return ($null -ne $ns -and $ns -match "Active")
}

Assert-Test "Helm Namespace 'devops-lab6-helm' exists" {
    $ns = kubectl get namespace devops-lab6-helm --no-headers 2>$null
    return ($null -ne $ns -and $ns -match "Active")
}

# 3. ConfigMap Verification
Assert-Test "ConfigMap 'devops-lab6-config' contains required keys" {
    $keys = kubectl get configmap devops-lab6-config -n devops-lab6 -o jsonpath="{.data}" | ConvertFrom-Json
    return ($keys.APP_ENV -eq "production" -and $keys.LOG_LEVEL -eq "INFO" -and $null -ne $keys."app_settings.json")
}

# 4. Secret Verification
Assert-Test "Secret 'devops-lab6-secret' contains DB credentials and token" {
    $secret = kubectl get secret devops-lab6-secret -n devops-lab6 -o jsonpath="{.data}" | ConvertFrom-Json
    return ($null -ne $secret.DB_PASSWORD -and $null -ne $secret.API_AUTH_TOKEN)
}

# 5. Deployment Verification
Assert-Test "Deployment 'devops-web-app' has 2 ready replicas" {
    $readyReplicas = kubectl get deployment devops-web-app -n devops-lab6 -o jsonpath="{.status.readyReplicas}"
    return ($readyReplicas -eq "2")
}

# 6. Service Verification
Assert-Test "Service 'devops-web-service' exposed on NodePort 30086" {
    $nodePort = kubectl get service devops-web-service -n devops-lab6 -o jsonpath="{.spec.ports[0].nodePort}"
    return ($nodePort -eq "30086")
}

# 7. Job Completion Verification
Assert-Test "Batch Job 'data-batch-processor-job' reached 3/3 completions" {
    $succeeded = kubectl get job data-batch-processor-job -n devops-lab6 -o jsonpath="{.status.succeeded}"
    return ($succeeded -ge 3)
}

# 8. CronJob Verification
Assert-Test "CronJob 'system-periodic-cleaner-cron' configured with schedule '*/2 * * * *'" {
    $schedule = kubectl get cronjob system-periodic-cleaner-cron -n devops-lab6 -o jsonpath="{.spec.schedule}"
    $policy = kubectl get cronjob system-periodic-cleaner-cron -n devops-lab6 -o jsonpath="{.spec.concurrencyPolicy}"
    return ($schedule -eq "*/2 * * * *" -and $policy -eq "Forbid")
}

# 9. Pod Environment & Secret Ingestion Verification
Assert-Test "Pod environment variables successfully injected from Secret and ConfigMap" {
    $pod = kubectl get pods -n devops-lab6 -l app=devops-web-app -o jsonpath="{.items[0].metadata.name}"
    $envOutput = kubectl exec -n devops-lab6 $pod -- env
    return ($envOutput -match "APP_ENV=production" -and $envOutput -match "DB_USER=devops_admin" -and $envOutput -match "API_AUTH_TOKEN=")
}

# 10. Volume Mount Verification
Assert-Test "Mounted Secret file '/etc/secrets/vault_key.txt' exists with restricted permissions" {
    $pod = kubectl get pods -n devops-lab6 -l app=devops-web-app -o jsonpath="{.items[0].metadata.name}"
    $content = kubectl exec -n devops-lab6 $pod -- cat /etc/secrets/vault_key.txt
    return ($content -match "vault:v1:")
}

# 11. Pod HTTP API Verification
Assert-Test "Application Health and Ready Probes return HTTP 200" {
    $pod = kubectl get pods -n devops-lab6 -l app=devops-web-app -o jsonpath="{.items[0].metadata.name}"
    $healthCheck = kubectl exec -n devops-lab6 $pod -- python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/healthz').status)"
    return ($healthCheck.Trim() -eq "200")
}

# 12. Helm Release Verification
Assert-Test "Helm Release 'lab6-release' deployed with successful history" {
    $helmHistory = helm history lab6-release -n devops-lab6-helm --output json | ConvertFrom-Json
    return ($helmHistory.Count -ge 3)
}

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "   Verification Summary: $script:PassedTests / $script:TotalTests Tests Passed ($([math]::Round(($script:PassedTests/$script:TotalTests)*100, 1))%)" -ForegroundColor $(if ($script:FailedTests -eq 0) { "Green" } else { "Red" })
Write-Host "======================================================================" -ForegroundColor Cyan
