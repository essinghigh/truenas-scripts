# truenas-scripts
I cannot guarantee stability or availability of these scripts. I update them as needed for my own use but have decided to share them here in case they are useful to others.

## generate-forum-signature
Generates a forum signature with system information and pool layout (toplogy, width, size, available, flags for Metadata, Log, Cache, Spare, Dedup (MLCSD)).

This is very much a work in progress and will not handle specific pool configurations (i.e. mixed RAIDZ,MIRROR, possibly STRIPE, or mixed width mirror/raidz vdevs).

Usage:
```
curl -sSL https://raw.githubusercontent.com/essinghigh/truenas-scripts/main/generate-forum-signature/generate_forum_signature.bash | bash
```
Example forum signature:
```
TrueNAS Version: 25.04-BETA.1
CPU Model: Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz
Physical Memory: 125.7 GiB (Non-ECC)
Motherboard: ROG MAXIMUS X FORMULA
Pool: nvme | 1 x MIRROR | 2 wide | 944 GiB Total | 817.25 GiB Available |
Pool: data | 6 x MIRROR | 2 wide | 75.81 TiB Total | 57.03 TiB Available | C
```


## update-apps
Automatic updates for non-custom apps, uses webhooks for notifications.

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
