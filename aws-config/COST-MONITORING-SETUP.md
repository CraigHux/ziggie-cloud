# AWS Cost Monitoring Setup for Ziggie Ecosystem

> **Created**: 2025-12-27
> **Account**: 785186659442
> **Region**: eu-north-1 (SNS), us-east-1 (Budgets API)
> **Monthly Budget**: $150 (with buffer for heavy AI use)

---

## Quick Start

Run the setup script to configure all cost monitoring:

```powershell
cd C:\Ziggie\aws-config
.\setup-cost-monitoring.ps1
```

---

## Budget Configuration

### Budget: ziggie-monthly

| Setting | Value |
|---------|-------|
| **Budget Name** | ziggie-monthly |
| **Amount** | $150/month |
| **Type** | COST |
| **Period** | MONTHLY |
| **Start Date** | 2025-01-01 |

### Alert Thresholds

| Threshold | Amount | Type | Trigger |
|-----------|--------|------|---------|
| 50% | $75 | ACTUAL | When actual spend exceeds 50% |
| 80% | $120 | ACTUAL | When actual spend exceeds 80% |
| 100% | $150 | ACTUAL | When actual spend exceeds budget |
| 120% | $180 | FORECASTED | When forecasted spend exceeds 120% |

All alerts are sent to: `arn:aws:sns:eu-north-1:785186659442:ziggie-alerts`

---

## Cost Anomaly Detection

### Monitor: ziggie-cost-anomaly-monitor

- **Type**: DIMENSIONAL (monitors by service)
- **Alert Threshold**: Anomalies > $10
- **Frequency**: IMMEDIATE
- **Notifications**: SNS topic ziggie-alerts

This will alert you when:
- Unexpected spikes in any AWS service
- New services start incurring costs
- Usage patterns deviate from normal

---

## Viewing Cost Reports

### AWS Console Links

| Report | URL |
|--------|-----|
| **Cost Explorer** | https://console.aws.amazon.com/cost-management/home |
| **Budgets Dashboard** | https://console.aws.amazon.com/billing/home#/budgets |
| **Anomaly Detection** | https://console.aws.amazon.com/cost-management/home#/anomaly-detection |
| **Cost & Usage Reports** | https://console.aws.amazon.com/billing/home#/reports |

### CLI Commands

```powershell
$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$accountId = "785186659442"

# Get current month's costs
& $aws ce get-cost-and-usage `
    --time-period Start=2025-12-01,End=2025-12-31 `
    --granularity MONTHLY `
    --metrics BlendedCost `
    --region us-east-1

# Get costs by service
& $aws ce get-cost-and-usage `
    --time-period Start=2025-12-01,End=2025-12-31 `
    --granularity MONTHLY `
    --metrics BlendedCost `
    --group-by Type=DIMENSION,Key=SERVICE `
    --region us-east-1

# Check budget status
& $aws budgets describe-budget `
    --account-id $accountId `
    --budget-name ziggie-monthly `
    --region us-east-1

# List all budgets
& $aws budgets describe-budgets `
    --account-id $accountId `
    --region us-east-1

# Check anomaly monitors
& $aws ce get-anomaly-monitors --region us-east-1

# View detected anomalies (last 30 days)
& $aws ce get-anomalies `
    --date-interval Start=2025-11-27,End=2025-12-27 `
    --region us-east-1
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `budget-ziggie-monthly.json` | Budget definition ($150/month) |
| `budget-notifications.json` | Alert threshold configurations |
| `cost-anomaly-monitor.json` | Anomaly detection monitor definition |
| `cost-anomaly-subscription.json` | Anomaly alert subscription template |
| `setup-cost-monitoring.ps1` | One-command setup script |

---

## Monthly Cost Targets

| Usage Level | Target | Services |
|-------------|--------|----------|
| **Minimal** | $10-15 | VPS only (Hostinger) |
| **Normal** | $47-62 | VPS + AWS S3/Secrets/Lambda |
| **Heavy AI** | $150-200 | + GPU instances + Bedrock |

### Cost Breakdown by Service

| Service | Normal | Heavy AI | Notes |
|---------|--------|----------|-------|
| Hostinger VPS | $10 | $10 | Fixed monthly |
| AWS S3 | $2-5 | $5-10 | Asset storage |
| AWS Secrets Manager | $1 | $1 | API key vault |
| AWS Lambda | $0 | $1-5 | GPU auto-shutdown |
| AWS EC2 Spot (GPU) | $0 | $50-100 | g4dn.xlarge |
| AWS Bedrock | $0 | $20-50 | Claude/Nova |
| External APIs | $10-20 | $20-40 | Anthropic, OpenAI |

---

## Troubleshooting

### Budget Not Creating

```
Error: AccessDeniedException
```

Ensure your IAM user/role has these permissions:
- `budgets:CreateBudget`
- `budgets:DescribeBudgets`
- `budgets:ModifyBudget`

### Anomaly Detection Not Available

Cost Anomaly Detection requires:
1. Cost Explorer to be enabled (takes 24 hours after first enable)
2. At least 10 days of cost data

Enable Cost Explorer:
```powershell
& $aws ce get-cost-and-usage `
    --time-period Start=2025-12-01,End=2025-12-02 `
    --granularity DAILY `
    --metrics BlendedCost `
    --region us-east-1
```

### SNS Notifications Not Received

1. Verify SNS topic exists:
```powershell
& $aws sns list-topics --region eu-north-1
```

2. Check topic subscriptions:
```powershell
& $aws sns list-subscriptions-by-topic `
    --topic-arn arn:aws:sns:eu-north-1:785186659442:ziggie-alerts `
    --region eu-north-1
```

3. Subscribe your email:
```powershell
& $aws sns subscribe `
    --topic-arn arn:aws:sns:eu-north-1:785186659442:ziggie-alerts `
    --protocol email `
    --notification-endpoint your-email@example.com `
    --region eu-north-1
```

---

## IAM Permissions Required

Add to your IAM policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BudgetsAccess",
            "Effect": "Allow",
            "Action": [
                "budgets:CreateBudget",
                "budgets:DeleteBudget",
                "budgets:DescribeBudget",
                "budgets:DescribeBudgets",
                "budgets:ModifyBudget",
                "budgets:ViewBudget"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CostExplorerAccess",
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ce:GetCostForecast",
                "ce:GetAnomalyMonitors",
                "ce:CreateAnomalyMonitor",
                "ce:GetAnomalySubscriptions",
                "ce:CreateAnomalySubscription",
                "ce:GetAnomalies"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## Related Documentation

- AWS Budgets: https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html
- Cost Anomaly Detection: https://docs.aws.amazon.com/cost-management/latest/userguide/manage-ad.html
- Cost Explorer: https://docs.aws.amazon.com/cost-management/latest/userguide/ce-exploring-data.html

---

## Document Metadata

| Field | Value |
|-------|-------|
| Created | 2025-12-27 |
| Author | AWS Cost Management Agent |
| Status | READY FOR DEPLOYMENT |
| Related Gap | GAP-033 (Set up Cost Explorer alerts) |
