import argparse
import subprocess
import json
import requests
import os
import sys
import datetime

"""
Automated TrueNAS configuration backup utility.
Handles config backup creation via midclt API calls and file download.
Maintains versioned backups with timestamp and system version metadata.
"""

def midclt_runner(call_args):
    """Execute midclt command and handle errors.
    
    Args:
        call_args (list): midclt command arguments as list
        
    Returns:
        dict: Parsed JSON response from midclt
        
    Raises:
        SystemExit: On command failure or JSON decode error
    """
    try:
        result = subprocess.check_output(call_args, stderr=subprocess.STDOUT)
        return json.loads(result)
    except subprocess.CalledProcessError as e:
        print("Error executing command: {}".format(' '.join(call_args)))
        print("Output:", e.output.decode())
        sys.exit(1)
    except json.JSONDecodeError as e:
        print("JSON decode error. Output was:")
        print(result.decode())
        sys.exit(1)

def main():
    """Main backup execution flow.
    
    1. Parse command line arguments
    2. Get system version info
    3. Generate backup filename with metadata
    4. Initiate config backup via midclt API
    5. Retrieve download URL from response
    6. Download and save backup file
    """
    parser = argparse.ArgumentParser(description="Automagically backup TrueNAS config file using midclt.")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to save the backup file. Will be created if it does not exist."
    )
    args = parser.parse_args()
    
    # Get TrueNAS version for filename and debugging
    try:
        with open('/etc/version', 'r') as f:
            truenas_version = f.read().strip()
    except Exception as e:
        print(f"Error reading TrueNAS version: {e}")
        truenas_version = "unknown"

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_filename = f"truenas-{truenas_version}-{timestamp}.tar"  # Format: truenas-<version>-<timestamp>.tar
    
    midclt_download_cmd = [
        "midclt", "call", "core.download",
        "config.save",
        '[{"secretseed": true, "root_authorized_keys": true}]',
        backup_filename
    ]
    print("Requesting download via midclt ...")
    download_json = midclt_runner(midclt_download_cmd)
    try:
        download_id = download_json[0]
        download_path = download_json[1]
    except (IndexError, KeyError):
        print("Unexpected response from midclt call: ", download_json)
        sys.exit(1)
    print("Download response received:")
    print("ID:", download_id)
    print("Path:", download_path)
    print("Retrieving UI port ...")
    general_config_cmd = ["midclt", "call", "system.general.config"]
    system_config = midclt_runner(general_config_cmd)
    ui_port = system_config.get("ui_port")
    if ui_port is None:
        print("Could not retrieve ui_port from system.general.config: ", system_config)
        sys.exit(1)
    print("UI port:", ui_port)
    download_url = f"http://localhost:{ui_port}{download_path}"
    print("Download URL:", download_url)
    
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    print("Downloading file ...")
    try:
        response = requests.get(download_url, verify=False, stream=True)
        response.raise_for_status()
        
        filename = backup_filename
        output_file = os.path.join(output_dir, filename)
        
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Download successful. File saved to: {output_file}")
    except requests.RequestException as e:
        print("Error downloading file:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
