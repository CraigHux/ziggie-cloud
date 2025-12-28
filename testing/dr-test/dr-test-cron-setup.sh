#!/bin/bash
#=============================================================================
# ZIGGIE DR TEST - CRON SETUP SCRIPT
#=============================================================================
# Purpose: Configure automated quarterly DR testing with notifications
# Run on: Hostinger VPS (82.25.112.73)
#
# This script sets up:
#   1. Quarterly DR test cron job
#   2. Email notifications on test completion
#   3. Slack webhook notifications (optional)
#   4. Test result archival
#
# Usage: ./dr-test-cron-setup.sh [--install | --uninstall | --test]
#
#=============================================================================

set -euo pipefail

# Configuration
DR_TEST_DIR="/opt/ziggie/testing/dr-test"
DR_TEST_SCRIPT="${DR_TEST_DIR}/run-full-dr-test.sh"
NOTIFICATION_SCRIPT="${DR_TEST_DIR}/dr-test-notify.sh"
LOG_DIR="${DR_TEST_DIR}/logs"
ARCHIVE_DIR="${DR_TEST_DIR}/archive"

# Notification settings (configure these)
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
AWS_SNS_TOPIC="${AWS_SNS_TOPIC:-}"

# Cron schedule: Quarterly on the first Sunday at 2 AM
# January 1, April 1, July 1, October 1
CRON_SCHEDULE="0 2 1 1,4,7,10 0"

#=============================================================================
# UTILITY FUNCTIONS
#=============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

create_directories() {
    log "Creating required directories..."
    mkdir -p "${DR_TEST_DIR}"
    mkdir -p "${LOG_DIR}"
    mkdir -p "${ARCHIVE_DIR}"
    chmod 755 "${DR_TEST_DIR}" "${LOG_DIR}" "${ARCHIVE_DIR}"
}

#=============================================================================
# NOTIFICATION SCRIPT GENERATION
#=============================================================================

create_notification_script() {
    log "Creating notification script..."

    cat > "${NOTIFICATION_SCRIPT}" << 'NOTIFY_EOF'
#!/bin/bash
#=============================================================================
# DR Test Notification Script
# Sends notifications via email, Slack, and/or AWS SNS
#=============================================================================

REPORT_FILE="$1"
LOG_FILE="$2"

# Read configuration from environment or defaults
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-}"
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
AWS_SNS_TOPIC="${AWS_SNS_TOPIC:-}"

# Extract test summary from report
if [ -f "$REPORT_FILE" ]; then
    PASSED=$(grep -oP 'Tests Passed.*\*\*\s*\K\d+' "$REPORT_FILE" 2>/dev/null || echo "0")
    FAILED=$(grep -oP 'Tests Failed.*\*\*\s*\K\d+' "$REPORT_FILE" 2>/dev/null || echo "0")
    SKIPPED=$(grep -oP 'Tests Skipped.*\*\*\s*\K\d+' "$REPORT_FILE" 2>/dev/null || echo "0")
    PASS_RATE=$(grep -oP 'Pass Rate.*\*\*\s*\K\d+' "$REPORT_FILE" 2>/dev/null || echo "0")

    if [ "$FAILED" -eq 0 ]; then
        STATUS="SUCCESS"
        EMOJI=":white_check_mark:"
    else
        STATUS="FAILED"
        EMOJI=":x:"
    fi
else
    STATUS="ERROR"
    EMOJI=":warning:"
    PASSED="N/A"
    FAILED="N/A"
    SKIPPED="N/A"
    PASS_RATE="N/A"
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
HOSTNAME=$(hostname)

#-----------------------------------------------------------------------------
# Email Notification
#-----------------------------------------------------------------------------
send_email() {
    if [ -n "$NOTIFICATION_EMAIL" ] && command -v mail &> /dev/null; then
        echo "Sending email notification..."

        SUBJECT="[Ziggie DR Test] ${STATUS} - ${TIMESTAMP}"

        cat << EMAIL_BODY | mail -s "$SUBJECT" "$NOTIFICATION_EMAIL"
Ziggie Disaster Recovery Test Report
=====================================

Test Status: ${STATUS}
Timestamp: ${TIMESTAMP}
Hostname: ${HOSTNAME}

Test Results:
- Passed: ${PASSED}
- Failed: ${FAILED}
- Skipped: ${SKIPPED}
- Pass Rate: ${PASS_RATE}%

Report Location: ${REPORT_FILE}
Log Location: ${LOG_FILE}

This is an automated notification from the Ziggie DR test system.
EMAIL_BODY

        echo "Email sent to ${NOTIFICATION_EMAIL}"
    fi
}

#-----------------------------------------------------------------------------
# Slack Notification
#-----------------------------------------------------------------------------
send_slack() {
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        echo "Sending Slack notification..."

        SLACK_PAYLOAD=$(cat << SLACK_JSON
{
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "${EMOJI} Ziggie DR Test ${STATUS}",
                "emoji": true
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Status:*\n${STATUS}"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Timestamp:*\n${TIMESTAMP}"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Passed:*\n${PASSED}"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Failed:*\n${FAILED}"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Skipped:*\n${SKIPPED}"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Pass Rate:*\n${PASS_RATE}%"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Host: ${HOSTNAME} | Report: ${REPORT_FILE}"
                }
            ]
        }
    ]
}
SLACK_JSON
)

        curl -s -X POST -H 'Content-type: application/json' \
            --data "$SLACK_PAYLOAD" \
            "$SLACK_WEBHOOK_URL"

        echo "Slack notification sent"
    fi
}

#-----------------------------------------------------------------------------
# AWS SNS Notification
#-----------------------------------------------------------------------------
send_sns() {
    if [ -n "$AWS_SNS_TOPIC" ] && command -v aws &> /dev/null; then
        echo "Sending AWS SNS notification..."

        MESSAGE="Ziggie DR Test ${STATUS}

Test Results:
- Passed: ${PASSED}
- Failed: ${FAILED}
- Skipped: ${SKIPPED}
- Pass Rate: ${PASS_RATE}%

Timestamp: ${TIMESTAMP}
Host: ${HOSTNAME}
Report: ${REPORT_FILE}"

        aws sns publish \
            --topic-arn "$AWS_SNS_TOPIC" \
            --subject "[Ziggie DR Test] ${STATUS}" \
            --message "$MESSAGE" \
            --region eu-north-1

        echo "SNS notification sent"
    fi
}

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
echo "=== DR Test Notification Script ==="
echo "Report: $REPORT_FILE"
echo "Status: $STATUS"
echo ""

send_email
send_slack
send_sns

echo "=== Notifications Complete ==="
NOTIFY_EOF

    chmod +x "${NOTIFICATION_SCRIPT}"
    log "Notification script created at ${NOTIFICATION_SCRIPT}"
}

#=============================================================================
# WRAPPER SCRIPT FOR CRON
#=============================================================================

create_cron_wrapper() {
    log "Creating cron wrapper script..."

    WRAPPER_SCRIPT="${DR_TEST_DIR}/dr-test-cron-wrapper.sh"

    cat > "${WRAPPER_SCRIPT}" << 'WRAPPER_EOF'
#!/bin/bash
#=============================================================================
# DR Test Cron Wrapper
# Called by cron to execute DR test and send notifications
#=============================================================================

set -euo pipefail

# Configuration
DR_TEST_DIR="/opt/ziggie/testing/dr-test"
LOG_DIR="${DR_TEST_DIR}/logs"
ARCHIVE_DIR="${DR_TEST_DIR}/archive"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Log file for this run
CRON_LOG="${LOG_DIR}/dr-test-cron-${TIMESTAMP}.log"

# Start logging
exec > >(tee -a "${CRON_LOG}") 2>&1

echo "=========================================="
echo "Ziggie DR Test - Automated Run"
echo "Started: $(date)"
echo "=========================================="

# Navigate to test directory
cd "${DR_TEST_DIR}"

# Run the DR test
./run-full-dr-test.sh --quiet

# Find the latest report
LATEST_REPORT=$(ls -t reports/dr-test-report-*.md 2>/dev/null | head -1)
LATEST_LOG=$(ls -t reports/dr-test-*.log 2>/dev/null | head -1)

# Send notifications
if [ -f "${DR_TEST_DIR}/dr-test-notify.sh" ]; then
    "${DR_TEST_DIR}/dr-test-notify.sh" "${LATEST_REPORT}" "${LATEST_LOG}"
fi

# Archive old reports (keep last 12 = 3 years of quarterly tests)
REPORT_COUNT=$(ls -1 reports/dr-test-report-*.md 2>/dev/null | wc -l)
if [ "$REPORT_COUNT" -gt 12 ]; then
    echo "Archiving old reports..."
    ls -t reports/dr-test-report-*.md | tail -n +13 | while read old_report; do
        mv "$old_report" "${ARCHIVE_DIR}/"
    done
fi

echo "=========================================="
echo "Completed: $(date)"
echo "Report: ${LATEST_REPORT}"
echo "=========================================="
WRAPPER_EOF

    chmod +x "${WRAPPER_SCRIPT}"
    log "Cron wrapper script created at ${WRAPPER_SCRIPT}"
}

#=============================================================================
# CRON INSTALLATION
#=============================================================================

install_cron() {
    log "Installing cron job for quarterly DR tests..."

    # Create the cron entry
    CRON_ENTRY="${CRON_SCHEDULE} ${DR_TEST_DIR}/dr-test-cron-wrapper.sh >> ${LOG_DIR}/dr-test-cron.log 2>&1"

    # Check if cron entry already exists
    if crontab -l 2>/dev/null | grep -q "dr-test-cron-wrapper.sh"; then
        log "Cron job already exists, updating..."
        crontab -l | grep -v "dr-test-cron-wrapper.sh" | crontab -
    fi

    # Add new cron entry
    (crontab -l 2>/dev/null; echo "# Ziggie Quarterly DR Test"; echo "$CRON_ENTRY") | crontab -

    log "Cron job installed successfully"
    log "Schedule: First Sunday of Jan, Apr, Jul, Oct at 2:00 AM"
    log ""
    log "Current crontab:"
    crontab -l | grep -A1 "Ziggie"
}

uninstall_cron() {
    log "Removing DR test cron job..."

    if crontab -l 2>/dev/null | grep -q "dr-test-cron-wrapper.sh"; then
        crontab -l | grep -v "dr-test-cron-wrapper.sh" | grep -v "Ziggie Quarterly DR Test" | crontab -
        log "Cron job removed successfully"
    else
        log "No DR test cron job found"
    fi
}

#=============================================================================
# TEST MODE
#=============================================================================

test_setup() {
    log "Testing DR test setup..."

    echo ""
    echo "=== Directory Check ==="
    ls -la "${DR_TEST_DIR}" 2>/dev/null || echo "Directory not found"

    echo ""
    echo "=== Script Check ==="
    [ -x "${DR_TEST_SCRIPT}" ] && echo "DR test script: OK" || echo "DR test script: MISSING"
    [ -x "${NOTIFICATION_SCRIPT}" ] && echo "Notification script: OK" || echo "Notification script: MISSING"
    [ -x "${DR_TEST_DIR}/dr-test-cron-wrapper.sh" ] && echo "Cron wrapper: OK" || echo "Cron wrapper: MISSING"

    echo ""
    echo "=== Cron Check ==="
    crontab -l 2>/dev/null | grep "dr-test" || echo "No DR test cron job found"

    echo ""
    echo "=== Notification Config ==="
    [ -n "${NOTIFICATION_EMAIL:-}" ] && echo "Email: Configured (${NOTIFICATION_EMAIL})" || echo "Email: Not configured"
    [ -n "${SLACK_WEBHOOK_URL:-}" ] && echo "Slack: Configured" || echo "Slack: Not configured"
    [ -n "${AWS_SNS_TOPIC:-}" ] && echo "AWS SNS: Configured (${AWS_SNS_TOPIC})" || echo "AWS SNS: Not configured"

    echo ""
    echo "=== Next Scheduled Run ==="
    # Calculate next quarterly date
    MONTH=$(date +%m)
    YEAR=$(date +%Y)
    case $MONTH in
        01|02|03) NEXT_MONTH="04"; NEXT_YEAR=$YEAR ;;
        04|05|06) NEXT_MONTH="07"; NEXT_YEAR=$YEAR ;;
        07|08|09) NEXT_MONTH="10"; NEXT_YEAR=$YEAR ;;
        10|11|12) NEXT_MONTH="01"; NEXT_YEAR=$((YEAR + 1)) ;;
    esac
    echo "Next scheduled: ${NEXT_YEAR}-${NEXT_MONTH}-01 (first Sunday at 02:00)"
}

#=============================================================================
# MAIN
#=============================================================================

show_usage() {
    echo "Usage: $0 [--install | --uninstall | --test]"
    echo ""
    echo "Options:"
    echo "  --install    Install cron job and create scripts"
    echo "  --uninstall  Remove cron job"
    echo "  --test       Test current setup"
    echo ""
    echo "Environment variables:"
    echo "  NOTIFICATION_EMAIL  Email address for notifications"
    echo "  SLACK_WEBHOOK_URL   Slack webhook URL for notifications"
    echo "  AWS_SNS_TOPIC       AWS SNS topic ARN for notifications"
}

main() {
    case "${1:-}" in
        --install)
            log "=== Installing Ziggie DR Test Automation ==="
            create_directories
            create_notification_script
            create_cron_wrapper
            install_cron
            log "=== Installation Complete ==="
            echo ""
            echo "Next steps:"
            echo "1. Configure notifications by setting environment variables:"
            echo "   export NOTIFICATION_EMAIL=your@email.com"
            echo "   export SLACK_WEBHOOK_URL=https://hooks.slack.com/..."
            echo "   export AWS_SNS_TOPIC=arn:aws:sns:..."
            echo ""
            echo "2. Run a test to verify: $0 --test"
            echo ""
            echo "3. For manual test run: ${DR_TEST_SCRIPT}"
            ;;
        --uninstall)
            log "=== Uninstalling Ziggie DR Test Automation ==="
            uninstall_cron
            log "=== Uninstallation Complete ==="
            log "Note: Scripts and logs were not removed"
            ;;
        --test)
            test_setup
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
