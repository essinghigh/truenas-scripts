# Persistent Crontab

TrueNAS updates reset crontab entries, causing scheduled tasks to stop working. The persistent-crontab script handles crontab backups and manages a post-init task that will automatically restore crontab configuration from a backup file after system updates.

## Usage

If you plan on using this to handle crontab backups (for which this script is overkill), run the script manually once before adding it as a cronjob. This will ensure the init script is created.
```
python3 persistent_crontab.py --crontab-backup-file /mnt/tank/backups/crontab.bak [--no-confirm]
```
## Flags

- `--crontab-backup-file`: Path where the crontab backup file will be saved (required). It's recommended to store this on a ZFS storage pool (e.g., in /mnt/tank) to ensure persistence.
- `--no-confirm`: Automatically update existing init scripts without confirmation if needed. Not recommended.

## How It Works

1. The script backs up your current crontab configuration to the specified file.
2. It creates a post-init script that will run on every system boot and restore your crontab from the backup file.
3. If you run the script again with a different backup path, it will ask if you want to update the existing init script (unless `--no-confirm` is used, in which case the script will create/update the init script without prompting).

## Example: Setting Up Automatic Crontab Backups

To ensure your crontab stays up-to-date in the backup file, you can add the script itself to your crontab. This creates a self-maintaining system where:
1. The script backs up your crontab regularly
2. The init script restores from backup after system updates

```
# First run the script manually to create the initial backup and init script
python3 /mnt/tank/scripts/truenas-scripts/persistent-crontab/persistent_crontab.py --crontab-backup-file /mnt/tank/backups/crontab.bak

# Then add this to your crontab (crontab -e) to keep the backup updated weekly
0 0 * * 0 /usr/bin/python3 /mnt/tank/scripts/truenas-scripts/persistent-crontab/persistent_crontab.py --crontab-backup-file /mnt/tank/backups/crontab.bak --no-confirm > /dev/null 2>&1
```

This setup ensures that:
- Your crontab is backed up weekly
- After any system update, the init script will restore your crontab from the backup
- If the init script is somehow removed, it will be recreated during the next crontab backup