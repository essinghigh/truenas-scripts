#!/bin/bash
set -euo pipefail
trap 'echo "Error occurred at line $LINENO" >&2; exit 1' ERR
log() { echo "[$(date)] $*"; }

# ---------------------------
# Configuration Management
# ---------------------------
CONFIG_FILE="$(dirname "$0")/update_apps.toml"
if [ -f "$CONFIG_FILE" ]; then
    config_hostname=$(grep '^hostname' "$CONFIG_FILE" | head -n 1 | awk -F'=' '{print $2}' | sed 's/[#].*//' | tr -d ' "')
    if [ -n "$config_hostname" ]; then
       hostname="$config_hostname"
    else
       hostname=$(hostname)
    fi
    discord_enabled=$(awk -F'=' '/\[discord\]/{flag=1} flag && /enabled/ {print $2; exit}' "$CONFIG_FILE" | tr -d ' "')
    discord_webhook=$(awk -F'=' '/\[discord\]/{flag=1} flag && /webhook_url/ {print $2; exit}' "$CONFIG_FILE" | tr -d ' "')
    slack_enabled=$(awk -F'=' '/\[slack\]/{flag=1} flag && /enabled/ {print $2; exit}' "$CONFIG_FILE" | tr -d ' "')
    slack_webhook=$(awk -F'=' '/\[slack\]/{flag=1} flag && /webhook_url/ {print $2; exit}' "$CONFIG_FILE" | tr -d ' "')
    exclude_apps_line=$(awk '/\[exclude\]/{flag=1} flag && /apps/ {print; exit}' "$CONFIG_FILE")
    exclude_apps_line=$(echo "$exclude_apps_line" | awk -F'=' '{print $2}' | sed 's/[][]//g; s/"//g')
    IFS=',' read -ra exclude_apps <<< "${exclude_apps_line}"
    debug_enabled=$(awk -F'=' '/\[debug\]/{flag=1} flag && /enabled/ {print $2; exit}' "$CONFIG_FILE" | tr -d ' "')
    dry_run=$(awk -F'=' '/\[debug\]/{flag=1} flag && /dry_run/ {print $2; exit}' "$CONFIG_FILE" | tr -d ' "')
else
    echo "Config file not found, proceeding with defaults."
    hostname=$(hostname)
    discord_enabled="false"
    slack_enabled="false"
    debug_enabled="false"
    dry_run="false"
fi

if [ "$debug_enabled" = "true" ]; then
    echo "DEBUG: Config loaded - hostname: $hostname, discord_enabled: $discord_enabled, slack_enabled: $slack_enabled, dry_run: $dry_run"
fi

log_content=""
upgrade_count=0

# ---------------------------
# Catalog Synchronization
# ---------------------------
log "Starting catalog sync..."
midclt call catalog.sync > /dev/null
log "-----------------------------------------"

# ---------------------------
# Check Available Upgrades
# ---------------------------
log "Checking for non-custom apps with available upgrades..."
apps_list=$(midclt call app.query | \
    jq -r '.[] |
           select(.custom_app != true and .upgrade_available == true) |
           "\(.name)\t\(.version)\t\(.upgrade_available)"')

if [ -z "$apps_list" ]; then
    log "No updates available for non-custom applications"
    log "-----------------------------------------"
    exit 0
fi

log "Found updates for the following apps:"
log "$apps_list" | awk -F'\t' '{print "• " $1 " (Current: " $2 ")"}'
log "-----------------------------------------"

# ---------------------------
# Process Upgrades
# ---------------------------
while IFS=$'\t' read -r app_name current_version has_update; do
    skip_app=false
    for e in "${exclude_apps[@]}"; do
        if [ "$app_name" = "${e// /}" ]; then
            skip_app=true
            break
        fi
    done
    if [ "$skip_app" = true ]; then
        log "Skipping excluded app: $app_name"
        log "-----------------------------------------"
        continue
    fi

    [ "$has_update" != "true" ] && continue

    log "Processing: $app_name"
    if [ "$debug_enabled" = "true" ]; then
        log "DEBUG: App $app_name - current version: $current_version, has_update: $has_update"
    fi

    log "   - Current version: $current_version"

    # ---------------------------
    # Perform Upgrade
    # ---------------------------
    if [ "$dry_run" = "true" ]; then
        log "   - Dry-run mode: not upgrading $app_name"
        new_version="$current_version (dry-run)"
        log_content+="$app_name | $current_version → $new_version\n"
        ((upgrade_count++))
    else
        if midclt call app.upgrade "$app_name" > /dev/null 2>&1; then
            new_version=$(midclt call app.config "$app_name" | jq -r '.ix_context.app_metadata.version // "unknown"')
            while [[ "$new_version" == "unknown" || "$new_version" == "$current_version" ]]; do
                sleep 5
                new_version=$(midclt call app.config "$app_name" | jq -r '.ix_context.app_metadata.version // "unknown"')
            done
            log "   - New version:    $new_version"
            log_content+="$app_name | $current_version → $new_version\n"
            ((upgrade_count++))
        fi
    fi

    log "-----------------------------------------"
done < <(echo "$apps_list")

# ---------------------------
# Final Status Reporting
# ---------------------------
log "Successfully upgraded $upgrade_count app(s)"

if [ "$discord_enabled" = "true" ]; then
    if [ "$dry_run" = "true" ]; then
        curl -s \
        -H "Content-Type: application/json" \
        -d "{\"content\":\"[$hostname] (Dry Run) Would have upgraded $upgrade_count app(s):\n$log_content\"}" \
        "$discord_webhook" > /dev/null 2>&1
    else
        curl -s \
        -H "Content-Type: application/json" \
        -d "{\"content\":\"[$hostname] Successfully upgraded $upgrade_count app(s):\n$log_content\"}" \
        "$discord_webhook" > /dev/null 2>&1
    fi
fi
if [ "$slack_enabled" = "true" ]; then
    if [ "$dry_run" = "true" ]; then
        curl -s \
        -H "Content-Type: application/json" \
        -d "{\"content\":\"[$hostname] (Dry Run) Would have upgraded $upgrade_count app(s):\n$log_content\"}" \
        "$slack_webhook" > /dev/null 2>&1
    else
        curl -s \
        -H "Content-Type: application/json" \
        -d "{\"content\":\"[$hostname] Successfully upgraded $upgrade_count app(s):\n$log_content\"}" \
        "$slack_webhook" > /dev/null 2>&1
    fi
fi

# ---------------------------
# Cleanup
# ---------------------------
log "Script execution completed"
exit 0
