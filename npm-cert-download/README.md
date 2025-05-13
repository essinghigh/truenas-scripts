# NPM Certificate Download

Downloads and extracts an NPM certificate along with its corresponding private key. This tool obtains a bearer token using provided credentials, downloads the certificate zip, and extracts the certificate and key files.

## Usage

```
python3 npm_cert_download.py --cert-file /path/to/cert.pem --key-file /path/to/key.pem --cert-id <certificate_id> --endpoint <NPM_management_endpoint> --username  --password
```

## Required Flags

- `--cert-file`: Path where the downloaded certificate will be saved (required).
- `--key-file`: Path where the downloaded private key will be saved (required).
- `--cert-id`: ID of the certificate to download (required).
- `--endpoint`: NPM Management Endpoint (e.g., http://<truenas-ip>:81) (not required if NPM_MGMT_ENDPOINT Environment Variable is set).
- `--username`: Username for NPM Management Portal (not required if NPM_USERNAME Environment Variable is set).
- `--password`: Password for NPM Management Portal (not required if NPM_PASSWORD Environment Variable is set).

## Optional Flags

- `--list-certs`: List available certificates. If this flag is provided, the script will list all certificates instead of downloading one.

## Obtaining the Certificate ID

To get the certificate ID, you can use the `--list-certs` flag. This will display a list of available certificates along with their IDs. For example:

```
python3 npm_cert_download.py --list-certs --endpoint <NPM_management_endpoint> --username  --password
```

This command will output a list of certificates in the following format:

```
ID | Domains | Provider

1  | *.example.com, example.com | Let's Encrypt
2  | anotherdomain.com | Let's Encrypt
```

You can then use the appropriate ID in the `--cert-id` flag when downloading a certificate.
