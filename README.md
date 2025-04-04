# TrueNAS Scripts
I cannot guarantee stability or availability of these scripts. I update them as needed for my own use but have decided to share them here in case they are useful to others.

## Table of Contents

- [generate-forum-signature](#generate-forum-signature)
- [update-apps](#update-apps)
- [configuration-backup](#configuration-backup)
- [npm-cert-download](#npm-certificate-download)

---

## Generate Forum Signature

Generates a forum signature with system information and pool layout (topology, width, size, available, flags for Metadata, Log, Cache, Spare, Dedup (MLCSD)).

> Note: This is very much a work in progress. The script does not handle specific pool configurations (e.g., mixed RAIDZ, MIRROR, possibly STRIPE, or mixed width mirror/raidz vdevs).

**Usage**

```
curl -sSL https://raw.githubusercontent.com/essinghigh/truenas-scripts/main/generate-forum-signature/generate_forum_signature.bash | bash
```

**Example Forum Signature**

```
TrueNAS Version: 25.04-BETA.1
CPU Model: Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz
Physical Memory: 125.7 GiB (Non-ECC)
Motherboard: ROG MAXIMUS X FORMULA
Pool: nvme | 1 x MIRROR | 2 wide | 944 GiB Total | 817.25 GiB Available |
Pool: data | 6 x MIRROR | 2 wide | 75.81 TiB Total | 57.03 TiB Available | C
```

---

## Update Apps

Automatic updates for non-custom apps using webhooks for notifications.

**Configuration**

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

Configuration options:

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

---

## Configuration Backup

Automates the backup of the TrueNAS configuration file using midclt. This script retrieves the TrueNAS version, downloads the configuration via midclt, and saves it as a tar file in the specified output directory.

**Usage**

```
python3 truenas-scripts/configuration-backup/configuration_backup.py --output-dir /path/to/backup
```

---

## NPM Certificate Download

Downloads and extracts an NPM certificate along with its corresponding private key. This tool obtains a bearer token using provided credentials, downloads the certificate zip, and extracts the certificate and key files.

**Usage**

```
python3 truenas-scripts/npm-cert-download/npm_cert_download.py --cert-file /path/to/cert.pem --key-file /path/to/key.pem --cert-id <certificate_id> --endpoint <NPM_management_endpoint> --username  --password
```


### Required Flags

- `--cert-file`: Path where the downloaded certificate will be saved (required).
- `--key-file`: Path where the downloaded private key will be saved (required).
- `--cert-id`: ID of the certificate to download (required).
- `--endpoint`: NPM Management Endpoint (e.g., http://\<truenas-ip\>:81) (not required if NPM_MGMT_ENDPOINT Environment Variable is set).
- `--username`: Username for NPM Management Portal (not required if NPM_USERNAME Environment Variable is set).
- `--password`: Password for NPM Management Portal (not required if NPM_PASSWORD Environment Variable is set).

### Optional Flags

- `--list-certs`: List available certificates. If this flag is provided, the script will list all certificates instead of downloading one.

### Obtaining the Certificate ID

To get the certificate ID, you can use the `--list-certs` flag. This will display a list of available certificates along with their IDs. For example:

```
python3 truenas-scripts/npm-cert-download/npm_cert_download.py --list-certs --endpoint <NPM_management_endpoint> --username  --password
```


This command will output a list of certificates in the following format:

```
ID | Domains | Provider

1  | *.example.com, example.com | Let's Encrypt
2  | anotherdomain.com | Let's Encrypt
```

You can then use the appropriate ID in the `--cert-id` flag when downloading a certificate.