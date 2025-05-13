# Update Apps

Automatic updates for non-custom apps using webhooks for notifications.

## Configuration

The script now uses a JSON config file (`update_apps.json`). If you have existing legacy TOML config, the script will automatically convert it to JSON format on the first run and remove the TOML file.

```json
{
  "hostname": "your-hostname",
  "discord": {
    "enabled": true,
    "webhook_url": "https://discord.com/api/webhooks/your-webhook"
  },
  "slack": {
    "enabled": false,
    "webhook_url": "https://hooks.slack.com/services/your-webhook"
  },
  "exclude": {
    "apps": ["pihole", "example"]
  },
  "debug": {
    "enabled": false,
    "dry_run": false
  }
}
```

## Configuration Options

- **hostname**: Hostname sent with the webhook notification. If unset, use the hostname of the system.
- **discord**: Settings for Discord notifications
  - **enabled**: Whether to send a webhook notification to Discord.
  - **webhook_url**: Webhook URL for Discord notifications.
- **slack**: Settings for Slack notifications
  - **enabled**: Whether to send a webhook notification to Slack.
  - **webhook_url**: Webhook URL for Slack notifications.
- **exclude**: 
  - **apps**: List of app names to exclude from updating.
- **debug**:
  - **enabled**: Whether to print debug messages to the console.
  - **dry_run**: Run the script without actually upgrading any apps; webhook notifications will still be sent.
