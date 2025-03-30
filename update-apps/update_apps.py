#!/usr/bin/env python3
import os
import sys
import json
import socket
import datetime
import subprocess
import re
import time
from pathlib import Path


def log(message: str) -> None:
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {message}")

def parse_toml(config_path: str) -> dict:
    """Parser for the TOML config file."""
    default_config = {
        "hostname": socket.gethostname(),
        "discord": {"enabled": False, "webhook_url": ""},
        "slack": {"enabled": False, "webhook_url": ""},
        "exclude": {"apps": []},
        "debug": {"enabled": False, "dry_run": False}
    }
    
    if not os.path.isfile(config_path):
        return default_config

    config = {
        "discord": {},
        "slack": {},
        "exclude": {},
        "debug": {}
    }
    current_section = None

    with open(config_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            section_match = re.match(r'\[(.*)\]', line)
            if section_match:
                current_section = section_match.group(1)
                continue

            if '=' in line:
                key, value = (item.strip() for item in line.split('=', 1))

                if current_section == "general" and key == "hostname":
                    config["hostname"] = value.strip('"')
                    continue

                if key == "apps" and current_section == "exclude":
                    match = re.search(r'\[(.*)\]', value)
                    if match:
                        apps_str = match.group(1)
                        config["exclude"]["apps"] = [app.strip(' "') for app in apps_str.split(',')]
                    continue

                if value.lower() in ("true", "false"):
                    parsed_value = (value.lower() == "true")
                else:
                    parsed_value = value.strip('"')

                if current_section in config:
                    config[current_section][key] = parsed_value

    if "hostname" not in config:
        config["hostname"] = socket.gethostname()

    return config


def run_command(command: str) -> str:
    """Run a shell command and return its standard output. Logs error if command fails."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if e.stderr:
            log(f"Command error: {e.stderr}")
        return ""


def send_webhook_notification(webhook_url: str, content: str) -> bool:
    """Send notification to a webhook (Discord or Slack)."""
    if not webhook_url:
        return False
    try:
        import requests
        headers = {'Content-Type': 'application/json'}
        payload = {'content': content}
        response = requests.post(webhook_url, headers=headers, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as error:
        log(f"Webhook notification error: {error}")
        return False


def upgrade_app(app: dict, config: dict, log_content: list, debug_enabled: bool, dry_run: bool) -> None:
    """Upgrade a single app if eligible."""
    app_name = app.get("name", "")
    current_version = app.get("version", "")

    if app_name in config.get("exclude", {}).get("apps", []):
        log(f"Skipping excluded app: {app_name}")
        log("-----------------------------------------")
        return

    log(f"Processing: {app_name}")
    if debug_enabled:
        log(f"DEBUG: App {app_name} - current version: {current_version}, has_update: {app.get('upgrade_available', False)}")
    log(f"   - Current version: {current_version}")

    if dry_run:
        log(f"   - Dry-run mode: not upgrading {app_name}")
        new_version = f"{current_version} (dry-run)"
        log_content.append(f"{app_name} | {current_version} → {new_version}")
    else:
        upgrade_result = run_command(f"midclt call app.upgrade \"{app_name}\"")
        if upgrade_result is not None:
            new_version = "unknown"
            max_attempts = 60
            attempts = 0
            while (new_version == "unknown" or new_version == current_version) and attempts < max_attempts:
                app_config = run_command(f"midclt call app.config \"{app_name}\"")
                if app_config:
                    config_data = json.loads(app_config)
                    new_version = config_data.get("ix_context", {}).get("app_metadata", {}).get("version", "unknown")
                if new_version == "unknown" or new_version == current_version:
                    time.sleep(5)
                    attempts += 1
            log(f"   - New version:    {new_version}")
            log_content.append(f"{app_name} | {current_version} → {new_version}")
    log("-----------------------------------------")


def main() -> int:
    """Main entry point for the update process."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, "update_apps.toml")
    config = parse_toml(config_file)

    hostname = config.get("hostname", socket.gethostname())
    debug_enabled = config.get("debug", {}).get("enabled", False)
    dry_run = config.get("debug", {}).get("dry_run", False)
    discord_enabled = config.get("discord", {}).get("enabled", False)
    discord_webhook = config.get("discord", {}).get("webhook_url", "")
    slack_enabled = config.get("slack", {}).get("enabled", False)
    slack_webhook = config.get("slack", {}).get("webhook_url", "")

    if debug_enabled:
        log(f"DEBUG: Config loaded - hostname: {hostname}, discord_enabled: {discord_enabled}, slack_enabled: {slack_enabled}, dry_run: {dry_run}")

    log("Starting catalog sync...")
    run_command("midclt call catalog.sync")
    log("-----------------------------------------")

    log("Checking for non-custom apps with available upgrades...")
    apps_json = run_command("midclt call app.query")
    if not apps_json:
        log("Failed to query apps")
        return 1

    apps_data = json.loads(apps_json)
    upgradable_apps = [
        app for app in apps_data
        if not app.get("custom_app", False) and app.get("upgrade_available", False)
    ]

    if not upgradable_apps:
        log("No updates available for non-custom applications")
        log("-----------------------------------------")
        return 0

    log("Found updates for the following apps:")
    for app in upgradable_apps:
        log(f"• {app.get('name', '')} (Current: {app.get('version', '')})")
    log("-----------------------------------------")

    total_upgrades = 0
    log_content = []
    for app in upgradable_apps:
        before_count = len(log_content)
        upgrade_app(app, config, log_content, debug_enabled, dry_run)
        if len(log_content) > before_count:
            total_upgrades += 1

    log(f"Successfully upgraded {total_upgrades} app(s)")

    if total_upgrades > 0:
        if discord_enabled:
            message = f"[{hostname}] "
            if dry_run:
                message += f"(Dry Run) Would have upgraded {total_upgrades} app(s):\n" + "\n".join(log_content)
            else:
                message += f"Successfully upgraded {total_upgrades} app(s):\n" + "\n".join(log_content)
            send_webhook_notification(discord_webhook, message)

        if slack_enabled:
            message = f"[{hostname}] "
            if dry_run:
                message += f"(Dry Run) Would have upgraded {total_upgrades} app(s):\n" + "\n".join(log_content)
            else:
                message += f"Successfully upgraded {total_upgrades} app(s):\n" + "\n".join(log_content)
            send_webhook_notification(slack_webhook, message)

    log("Script execution completed")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        log(f"Error: {e}")
        sys.exit(1)
