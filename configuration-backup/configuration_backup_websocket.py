import argparse
import os
import json
import subprocess
from truenas_api_client import Client
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Automated TrueNAS configuration backup utility.")
    parser.add_argument("--output-dir", required=True, help="Directory to save the backup file. Will be created if it does not exist.")
    args = parser.parse_args()

    token_cmd = ["midclt", "call", "auth.generate_token", "30", "{}", "false", "false"]
    result = subprocess.check_output(token_cmd, stderr=subprocess.STDOUT)
    token = result.decode().strip()
    # print("Generated token:", token)

    ui_port_cmd = ["midclt", "call", "system.general.config"]
    result = subprocess.check_output(ui_port_cmd, stderr=subprocess.STDOUT)
    ui_port = json.loads(result.decode().strip()).get("ui_port")
    # print("UI port:", ui_port)

    with Client(uri=f"ws://localhost:{ui_port}/websocket") as c:
        result = c.call("auth.login_with_token", token)
        print("Login result:", result)

        try:
            with open('/etc/version', 'r') as f:
                truenas_version = f.read().strip()
        except Exception as e:
            print(f"Error reading TrueNAS version: {e}")
            truenas_version = "unknown"

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_filename = f"truenas-{truenas_version}-{timestamp}.tar"

        config_result = c.call("core.download", "config.save", [{"secretseed": True, "root_authorized_keys": True}], backup_filename)
        # print("Config result:", config_result)
        download_path = config_result[1]

        download_url = f"http://localhost:{ui_port}{download_path}"
        # print("Download URL:", download_url)

        import requests
        response = requests.get(download_url, verify=False, stream=True)
        response.raise_for_status()

        output_file = os.path.join(args.output_dir, backup_filename)
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Download successful. File saved to: {output_file}")

if __name__ == "__main__":
    main()