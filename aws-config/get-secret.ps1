# AWS Secrets Manager Helper Script
# Usage: .\get-secret.ps1 -SecretName "ziggie/anthropic-api-key"

param(
    [Parameter(Mandatory=$true)]
    [string]$SecretName
)

$aws = "C:\Program Files\Amazon\AWSCLIV2\aws.exe"
$secret = & $aws secretsmanager get-secret-value --secret-id $SecretName --region eu-north-1 --query SecretString --output text

if ($LASTEXITCODE -eq 0) {
    Write-Output $secret
} else {
    Write-Error "Failed to retrieve secret: $SecretName"
    exit 1
}
