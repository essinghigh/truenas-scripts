# truenas-scripts
I cannot guarantee stability or availability of these scripts. I update them as needed for my own use but have decided to share them here in case they are useful to others.

## update-apps
Automatic updates for non-custom apps, uses Discord Webhook for notifications.
Configuration:
```
General:
hostname: Hostname sent with the webhook notification. If unset, use the hostname of the system.

Discord:
enabled: Whether to send a webhook notification to Discord.
webhook_url: Webhook URL to send the notification to.

Slack:
enabled: Whether to send a webhook notification to Slack.
webhook_url: Webhook URL to send the notification to.

Exclude:
apps: List of apps to exclude from updating.

Debug:
enabled: Whether to print debug messages to the console.
dry_run: Run the script without actually upgrading any apps, webhook notifications will still be sent.
```