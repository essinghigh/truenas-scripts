# Generate Forum Signature

Generates a forum signature with system information and pool layout (topology, width, size, available, flags for Metadata, Log, Cache, Spare, Dedup (MLCSD)).

> Note: This is very much a work in progress. The script does not handle specific pool configurations (e.g., mixed RAIDZ, MIRROR, possibly STRIPE, or mixed width mirror/raidz vdevs).

## Usage

```
curl -sSL https://raw.githubusercontent.com/essinghigh/truenas-scripts/main/generate-forum-signature/generate_forum_signature.bash | bash
```

## Example Forum Signature

```
TrueNAS Version: 25.04-BETA.1
CPU Model: Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz
Physical Memory: 125.7 GiB (Non-ECC)
Motherboard: ROG MAXIMUS X FORMULA
Pool: nvme | 1 x MIRROR | 2 wide | 944 GiB Total | 817.25 GiB Available |
Pool: data | 6 x MIRROR | 2 wide | 75.81 TiB Total | 57.03 TiB Available | C
```
