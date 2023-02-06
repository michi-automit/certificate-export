import os
import time
from prometheus_client import start_http_server, Gauge
import ssl
import certifi
import kubernetes
from kubernetes import client, config

# Load kubernetes config from default location
config.load_kube_config()

def get_certificate_expiration_time():
    try:
        v1 = client.CoreV1Api()
        secrets = v1.list_secret_for_all_namespaces()

        for secret in secrets.items:
            if secret.type == "kubernetes.io/tls":
                cert = secret.data["tls.crt"]
                certificate = ssl.get_server_certificate((secret.metadata.namespace, cert))
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)
                expiry_timestamp = x509.get_notAfter()
                return int(time.mktime(time.strptime(expiry_timestamp.decode(), '%Y%m%d%H%M%SZ')))
    except Exception as e:
        print("An error occured while fetching secrets: ", e)
        return None

expiration_time = Gauge('certificate_expiration_time', 'Time in seconds until the certificate expires')

if __name__ == '__main__':
    start_http_server(int(os.environ.get('PORT', 9091)))
    while True:
        expiration_timestamp = get_certificate_expiration_time()
        if expiration_timestamp is not None:
            expiration_time.set(expiration_timestamp)
        time.sleep(21600)