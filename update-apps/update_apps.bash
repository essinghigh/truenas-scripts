#!/bin/bash

hostname=$(hostname)
log_content=""
upgrade_count=0

# ---------------------------
# Catalog Synchronization
# ---------------------------
echo "[$(date)] Starting catalog sync..."
midclt call catalog.sync > /dev/null
echo "-----------------------------------------"

# ---------------------------
# Check Available Upgrades
# ---------------------------
echo "[$(date)] Checking for non-custom apps with available upgrades..."
apps_list=$(midclt call app.query | \
    jq -r '.[] |
           select(.custom_app != true and .upgrade_available == true) |
           "\(.name)\t\(.version)\t\(.upgrade_available)"')

if [ -z "$apps_list" ]; then
    echo "[$(date)] No updates available for non-custom applications"
    echo "-----------------------------------------"
    exit 0
fi

echo "[$(date)] Found updates for the following apps:"
echo "$apps_list" | awk -F'\t' '{print "• " $1 " (Current: " $2 ")"}'
echo "-----------------------------------------"

# ---------------------------
# Process Upgrades
# ---------------------------
while IFS=$'\t' read -r app_name current_version has_update; do
    [ "$has_update" != "true" ] && continue

    echo "[$(date)] Processing: $app_name"
    echo "   - Current version: $current_version"

    # ---------------------------
    # Perform Upgrade
    # ---------------------------
    if midclt call app.upgrade "$app_name" > /dev/null 2>&1; then
        new_version=$(midclt call app.config "$app_name" | jq -r '.ix_context.app_metadata.version // "unknown"')
        while [[ "$new_version" == "unknown" || "$new_version" == "$current_version" ]]; do
            sleep 5
            new_version=$(midclt call app.config "$app_name" | jq -r '.ix_context.app_metadata.version // "unknown"')
        done
        echo "   - New version:    $new_version"
        log_content+="$app_name | $current_version → $new_version\n"
        ((upgrade_count++))
    fi

    echo "-----------------------------------------"
done < <(echo "$apps_list")

# ---------------------------
# Final Status Reporting
# ---------------------------
echo "[$(date)] Successfully upgraded $upgrade_count app(s)"
curl -s \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"[$hostname] Successfully upgraded $upgrade_count app(s):\n$log_content\"}" \
  "https://discord.com/api/webhooks/meow" > /dev/null 2>&1

# ---------------------------
# Cleanup
# ---------------------------
echo "[$(date)] Script execution completed"
exit 0
