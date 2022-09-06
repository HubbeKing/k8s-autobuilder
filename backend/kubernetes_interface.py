from datetime import datetime
from kubernetes import client, config
from kubernetes.client.models.v1_job import V1Job
from kubernetes.client.models.v1_job_list import V1JobList
from kubernetes.client.rest import ApiException
import logging
import os
from typing import Optional


# authn/authz setup for k8s client
if os.environ.get("K8S_AUTOBUILDER_IN_CLUSTER", False):
    config.load_incluster_config()
elif os.environ.get("K8S_AUTOBUILDER_KUBE_CONFIG", False):
    config.load_kube_config()
elif os.environ.get("K8S_AUTOBUILDER_MANUAL_KUBE_CONFIG", False):
    host = os.environ.get("K8S_AUTOBUILDER_KUBE_HOST")
    verify_ssl = bool(os.environ.get("K8S_AUTOBUILDER_KUBE_VERIFY_SSL"))
    ssl_cert_path = os.environ.get("K8S_AUTOBUILDER_KUBE_SSL_CA_CERT")
    token = os.environ.get("K8S_AUTOBUILDER_KUBE_TOKEN")

    configuration = client.Configuration()
    configuration.host = host
    configuration.verify_ssl = verify_ssl
    if verify_ssl:
        configuration.ssl_ca_cert = ssl_cert_path
    configuration.api_key = {"Authorization": f"Bearer {token}"}
    client = client.ApiClient(configuration)

logger = logging.getLogger("k8s_autobuilder.backend.kubernetes_interface")


def ensure_crds_exist() -> bool:
    """
    Create CRDs used by application (AutobuilderRepo, AutobuilderTemplate)
    """
    # TODO write CRD manifests from example files
    # TODO ensure CRDs exist in cluster, attempt to create them if not
    # ApiextensionsV1Api - list_custom_resource_definition
    # ApiextensionsV1Api - create_custom_resource_definition
    pass


def get_autobuilder_repo_config_by_name(repo_name: str) -> Optional[dict]:
    # TODO return parsed AutobuilderRepo object as dict - Get
    # CustomObjectsApi - get_cluster_custom_object
    pass


def get_autobuilder_repo_config_by_url(repo_url: str) -> Optional[dict]:
    # TODO return parsed AutobuilderRepo object as dict
    # CustomObjectsApi - get_cluster_custom_object
    pass


def get_autobuilder_template(template_name: str) -> Optional[dict]:
    # TODO return parsed AutobuilderTemplate object as dict
    # CustomObjectsApi - get_cluster_custom_object
    # TODO ensure it can be turned into a valid Job?
    pass


def get_secret_string(namespace: str, secret_ref: str, key: str) -> str:
    # TODO get and decode secret data from cluster
    pass


def create_job(namespace: str, job: dict) -> Optional[V1Job]:
    batch_api = client.BatchV1Api()
    try:
        job_object = batch_api.create_namespaced_job(
            body=job,
            namespace=namespace
        )
        return job_object
    except ApiException:
        logger.exception("Failed to create job resource!")
        return None


def get_job_logs(namespace: str, job_name: str) -> str:
    core_api = client.CoreV1Api()
    try:
        logs = core_api.read_namespaced_pod_log(
            name=job_name,
            namespace=namespace
        )
        return logs
    except ApiException:
        logger.exception("Failed to retrieve job logs!")
        return "Failed to retrieve job logs!"


def get_job(namespace: str, job_name: str) -> Optional[V1Job]:
    batch_api = client.BatchV1Api()
    try:
        job = batch_api.read_namespaced_job(
            name=job_name,
            namespace=namespace
        )
        return job
    except ApiException:
        logger.exception("Failed to retrieve job!")
        return None


def list_repo_jobs(namespace: str, repo_name: str) -> Optional[V1JobList]:
    batch_api = client.BatchV1Api()
    try:
        jobs = batch_api.list_namespaced_job(
            label_selector=f"hubbeking.k8s.autobuilder/repoName={repo_name}",
            namespace=namespace
        )
        return jobs
    except ApiException:
        logger.exception("Failed to retrieve job list!")
        return None


def get_latest_repo_job(namespace: str, repo_name: str) -> Optional[V1Job]:
    batch_api = client.BatchV1Api()
    try:
        jobs = batch_api.list_namespaced_job(
            label_selector=f"hubbeking.k8s.autobuilder/repoName={repo_name}",
            namespace=namespace
        )
        latest_job = None
        for job in jobs["items"]:
            build_date = datetime.fromisoformat(job.metadata["labels"]["hubbeking.k8s.autobuilder/buildDate"])
            if latest_job is None or build_date > latest_job.metadata["labels"]["hubbeking.k8s.autobuilder/buildDate"]:
                latest_job = job
        return latest_job
    except ApiException:
        logger.exception("Failed to retrieve job resource!")
        return None
