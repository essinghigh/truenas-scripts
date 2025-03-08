import requests
import re
import zipfile
import io
from OpenSSL import crypto
import os
import argparse

DEFAULT_NPM_MGMT_ENDPOINT = os.getenv('NPM_MGMT_ENDPOINT')
DEFAULT_USERNAME = os.getenv('NPM_USERNAME')
DEFAULT_PASSWORD = os.getenv('NPM_PASSWORD')

def get_bearer_token(username, password):
    url = f'{NPM_MGMT_ENDPOINT}/api/tokens'
    data = {
        'identity': username,
        'secret': password
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get('token')
    else:
        raise Exception(f"Failed to authenticate: {response.text}")

def download_certificate(token, cert_id):
    url = f'{NPM_MGMT_ENDPOINT}/api/nginx/certificates/{cert_id}/download'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download certificate: {response.text}")

def read_certificates(zip_content):
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        cert_filename = None
        key_filename = None
        for filename in z.namelist():
            if re.match(r'fullchain\d+\.pem', filename):
                cert_filename = filename
            elif re.match(r'privkey\d+\.pem', filename):
                key_filename = filename
        if cert_filename is None:
            raise Exception("No certificate file found matching the pattern 'fullchain\\d+\\.pem'.")
        if key_filename is None:
            raise Exception("No private key file found matching the pattern 'privkey\\d+\\.pem'.")
        with z.open(cert_filename) as cert_file:
            cert_data = cert_file.read()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
            cn = cert.get_subject().CN
            with z.open(key_filename) as key_file:
                private_key_data = key_file.read()
            return cert_data, private_key_data, cn

def list_certificates(token):
    url = f'{NPM_MGMT_ENDPOINT}/api/nginx/certificates?expand=owner'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        certificates = response.json()
        print("ID | Domains | Provider")
        print("-" * 50)
        for cert in certificates:
            print(f"{cert['id']} | {cert['nice_name']} | {cert['provider']}")
    else:
        raise Exception(f"Failed to list certificates: {response.text}")

def main():
    parser = argparse.ArgumentParser(description='NPM Certificate Download Tool')
    parser.add_argument('--list-certs', action='store_true', help='List available certificates')
    parser.add_argument('--endpoint', help='NPM Management Endpoint (e.g., http://<truenas-ip>:81)')
    parser.add_argument('--username', help='Username for NPM Management Portal')
    parser.add_argument('--password', help='Password for NPM Management Portal')
    parser.add_argument('--cert-file', help='Path where the downloaded certificate will be saved')
    parser.add_argument('--key-file', help='Path where the downloaded private key will be saved')
    parser.add_argument('--cert-id', type=int, help='ID of the certificate to download')
    args = parser.parse_args()

    global NPM_MGMT_ENDPOINT, USERNAME, PASSWORD, CERT_FILE, KEY_FILE, CERT_ID
    
    NPM_MGMT_ENDPOINT = args.endpoint or DEFAULT_NPM_MGMT_ENDPOINT
    USERNAME = args.username or DEFAULT_USERNAME
    PASSWORD = args.password or DEFAULT_PASSWORD
    
    if not NPM_MGMT_ENDPOINT:
        parser.error("NPM Management Endpoint is required. Provide it with --endpoint or set NPM_MGMT_ENDPOINT environment variable.")
    if not USERNAME:
        parser.error("Username is required. Provide it with --username or set NPM_USERNAME environment variable.")
    if not PASSWORD:
        parser.error("Password is required. Provide it with --password or set NPM_PASSWORD environment variable.")
    try:
        token = get_bearer_token(USERNAME, PASSWORD)
        if args.list_certs:
            list_certificates(token)
        else:
            CERT_FILE = args.cert_file
            KEY_FILE = args.key_file
            CERT_ID = args.cert_id
            if not CERT_FILE:
                parser.error("Certificate file path is required. Provide it with --cert-file.")
            if not KEY_FILE:
                parser.error("Key file path is required. Provide it with --key-file.")            
            if not CERT_ID:
                parser.error("Certificate ID is required. Provide it with --cert-id.")
            os.makedirs(os.path.dirname(CERT_FILE), exist_ok=True)
            os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
            zip_content = download_certificate(token, CERT_ID)
            cert_data, private_key_data, cn = read_certificates(zip_content)
            with open(CERT_FILE, 'wb') as cert_file:
                cert_file.write(cert_data)
            with open(KEY_FILE, 'wb') as key_file:
                key_file.write(private_key_data)
            print(f"Certificate for {cn} has been downloaded successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
