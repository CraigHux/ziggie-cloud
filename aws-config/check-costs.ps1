# AWS Cost Check Script
# Quickly view current month's costs and budget status
# Usage: .\check-costs.ps1
#
# Created: 2025-12-27

$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$accountId = "785186659442"

# Get current date info
$today = Get-Date
$startOfMonth = Get-Date -Day 1 -Hour 0 -Minute 0 -Second 0
$endOfMonth = $startOfMonth.AddMonths(1)

$startStr = $startOfMonth.ToString("yyyy-MM-dd")
$endStr = $endOfMonth.ToString("yyyy-MM-dd")

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         ZIGGIE AWS COST REPORT - $($today.ToString('MMMM yyyy'))" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Get total costs for the month
Write-Host "CURRENT MONTH COSTS:" -ForegroundColor Yellow
try {
    $costs = & $aws ce get-cost-and-usage `
        --time-period Start=$startStr,End=$endStr `
        --granularity MONTHLY `
        --metrics BlendedCost `
        --region us-east-1 `
        --output json | ConvertFrom-Json

    if ($costs.ResultsByTime -and $costs.ResultsByTime.Count -gt 0) {
        $totalCost = [math]::Round([double]$costs.ResultsByTime[0].Total.BlendedCost.Amount, 2)
        $unit = $costs.ResultsByTime[0].Total.BlendedCost.Unit
        Write-Host "  Total: `$$totalCost $unit" -ForegroundColor Green

        # Calculate percentage of budget
        $budgetLimit = 150
        $percentUsed = [math]::Round(($totalCost / $budgetLimit) * 100, 1)
        Write-Host "  Budget: `$$budgetLimit (${percentUsed}% used)" -ForegroundColor $(if ($percentUsed -gt 80) { "Red" } elseif ($percentUsed -gt 50) { "Yellow" } else { "Green" })
    } else {
        Write-Host "  No cost data available yet" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Failed to retrieve costs: $_" -ForegroundColor Red
}

Write-Host ""

# Get costs by service
Write-Host "COSTS BY SERVICE:" -ForegroundColor Yellow
try {
    $servicesCosts = & $aws ce get-cost-and-usage `
        --time-period Start=$startStr,End=$endStr `
        --granularity MONTHLY `
        --metrics BlendedCost `
        --group-by Type=DIMENSION,Key=SERVICE `
        --region us-east-1 `
        --output json | ConvertFrom-Json

    if ($servicesCosts.ResultsByTime -and $servicesCosts.ResultsByTime[0].Groups) {
        $services = $servicesCosts.ResultsByTime[0].Groups | Sort-Object { [double]$_.Metrics.BlendedCost.Amount } -Descending

        foreach ($service in $services) {
            $serviceName = $service.Keys[0]
            $amount = [math]::Round([double]$service.Metrics.BlendedCost.Amount, 2)
            if ($amount -gt 0.01) {
                Write-Host "  $serviceName : `$$amount" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "  No service-level data available" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Failed to retrieve service costs: $_" -ForegroundColor Red
}

Write-Host ""

# Check budget status
Write-Host "BUDGET STATUS:" -ForegroundColor Yellow
try {
    $budget = & $aws budgets describe-budget `
        --account-id $accountId `
        --budget-name ziggie-monthly `
        --region us-east-1 `
        --output json 2>$null | ConvertFrom-Json

    if ($budget.Budget) {
        $limit = $budget.Budget.BudgetLimit.Amount
        $actual = $budget.Budget.CalculatedSpend.ActualSpend.Amount
        $forecast = $budget.Budget.CalculatedSpend.ForecastedSpend.Amount

        Write-Host "  Budget Limit: `$$limit" -ForegroundColor Gray
        Write-Host "  Actual Spend: `$$([math]::Round([double]$actual, 2))" -ForegroundColor Green
        if ($forecast) {
            Write-Host "  Forecasted: `$$([math]::Round([double]$forecast, 2))" -ForegroundColor $(if ([double]$forecast -gt [double]$limit) { "Red" } else { "Yellow" })
        }
    }
} catch {
    Write-Host "  Budget 'ziggie-monthly' not found" -ForegroundColor Yellow
    Write-Host "  Run .\setup-cost-monitoring.ps1 to create it" -ForegroundColor Gray
}

Write-Host ""

# Check for anomalies
Write-Host "RECENT ANOMALIES:" -ForegroundColor Yellow
try {
    $thirtyDaysAgo = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
    $todayStr = $today.ToString("yyyy-MM-dd")

    $anomalies = & $aws ce get-anomalies `
        --date-interval Start=$thirtyDaysAgo,End=$todayStr `
        --region us-east-1 `
        --output json 2>$null | ConvertFrom-Json

    if ($anomalies.Anomalies -and $anomalies.Anomalies.Count -gt 0) {
        foreach ($anomaly in $anomalies.Anomalies) {
            $impact = [math]::Round([double]$anomaly.Impact.TotalImpact, 2)
            Write-Host "  - `$$impact anomaly detected" -ForegroundColor Red
        }
    } else {
        Write-Host "  No anomalies detected (last 30 days)" -ForegroundColor Green
    }
} catch {
    Write-Host "  Anomaly detection not configured" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "View full details at:" -ForegroundColor White
Write-Host "  https://console.aws.amazon.com/cost-management/home" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
