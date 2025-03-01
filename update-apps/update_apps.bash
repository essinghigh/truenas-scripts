#!/bin/bash
# Legacy script to ensure compatibility with old versions.

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
python3 "$SCRIPT_DIR/update_apps.py"