from datetime import datetime
from kubernetes import client, config
from kubernetes.client.models.v1_job import V1Job
from kubernetes.client.models.v1_job_status import V1JobStatus
from kubernetes.client.rest import ApiException
import logging
from typing import Optional

# TODO support other types of config (kubeconfig file, OAuth, etc)
config.load_incluster_config()
logger = logging.getLogger("k8s_autobuilder.backend.kubernetes_interface")


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


def get_job_status(namespace: str, job_name: str) -> Optional[V1JobStatus]:
    batch_api = client.BatchV1Api()
    try:
        job = batch_api.read_namespaced_job_status(
            name=job_name,
            namespace=namespace
        )
        return job.status
    except ApiException:
        logger.exception("Failed to retrieve job pod status!")
        return None


def get_latest_repo_job(namespace: str, repo_name: str) -> Optional[V1Job]:
    batch_api = client.BatchV1Api()
    try:
        jobs = batch_api.list_namespaced_job(
            label_selector=f"hubbeking.k8s.autobuilder/repo_name={repo_name}",
            namespace=namespace
        )
        latest_timestamp = datetime.min
        latest_job = None
        for job in jobs["items"]:
            build_date = datetime.fromisoformat(job["metadata"]["labels"]["hubbeking.k8s.autobuilder/build_date"])
            if build_date > latest_timestamp:
                latest_timestamp = build_date
                latest_job = job
        return latest_job
    except ApiException:
        logger.exception("Failed to retrieve job resource!")
        return None
