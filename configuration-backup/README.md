# Configuration Backup

Automates the backup of the TrueNAS configuration file using the websocket API and saves it as a tar file in the specified output directory.

## Usage

```
python3 configuration_backup_websocket.py --output-dir /path/to/backup
```

## Example Cron Job

To run the backup automatically at 3 AM daily:

```
0 3 * * * /usr/bin/python3 /mnt/data/bin/truenas-scripts/configuration-backup/configuration_backup_websocket.py --output-dir /mnt/tank/dataset > /dev/null
```
