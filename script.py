#python3.9
from kubernetes import client, config
from datetime import datetime, timedelta
import time
import base64
import prometheus_client
from cryptography import x509
from cryptography.hazmat.backends import default_backend
print("init")
print("foo")
# Load Kubernetes Configuration
config.load_incluster_config()

# Initialize Kubernetes API Client
v1 = client.CoreV1Api()

# Prometheus Metric for Remaining Valid Days
remaining_valid_days = prometheus_client.Gauge(
    'remaining_valid_days', 'Remaining Valid Days for Kubernetes Secrets of Type "kubernetes.io/tls"', ['secret_name', 'secret_index', 'kubernetes_namespace'])

# Function to Retrieve and Update Prometheus Metrics
def update_metrics():

    secrets = v1.list_secret_for_all_namespaces().items

    # Loop Through Each Secret
    for secret in secrets:
        # Check if Secret is of Type "kubernetes.io/tls"
        if secret.type == "kubernetes.io/tls":
            namespace = secret.metadata.namespace
            secret_name = secret.metadata.name
            secret_index = 0
            print("Secret: " + secret_name)
            certs = base64.b64decode(secret.data["tls.crt"]).decode("utf-8")
            not_before, not_after = None, None
            certificates = certs.split("-----END CERTIFICATE-----")
            certificates = [c + "-----END CERTIFICATE-----" for c in certificates if len(c) > 1]
            for crt in certificates:
                cert = x509.load_pem_x509_certificate(crt.encode(), default_backend())
                valid_from = cert.not_valid_before
                valid_to = cert.not_valid_after
                today = datetime.now()

                print("Secret_Index: " + str(secret_index))

                remaining_time = valid_to - today
                remaining_days = remaining_time.days
                print(remaining_days)
                print(f"Das Zertifikat ist gültig von {valid_from} bis {valid_to}. " + namespace, secret_name)

                remaining_valid_days.labels(secret_name, secret_index, namespace).set(remaining_days)
                
                secret_index +=1


if __name__ == '__main__':
    prometheus_client.start_http_server(8000)
    while True:
        update_metrics()
        time.sleep(21600)