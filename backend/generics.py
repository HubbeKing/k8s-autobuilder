import datetime

from kubernetes.client.models.v1_job_status import V1JobStatus
import logging
import os
import sys
from typing import Optional
import yaml

logger = logging.getLogger("k8s.backend.generics")
config = {}


def load_config():
    config_path = os.environ.get("K8S_AUTOBUILDER_CONFIG", "/config.yaml")
    with open(config_path) as config_file:
        # load file with full YAML language, we can assume config file is trusted input, since it's up to the user to create it
        global config
        config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
        logger.debug(f"Loaded configuration {config}")


def setup_logging():
    root_logger = logging.getLogger()
    if int(os.environ.get("FLASK_DEBUG", 0)) == 1:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%H:%M:%S'))
    root_logger.addHandler(stream_handler)


def get_repo_config_by_name(repo_name: str) -> Optional[dict]:
    for repo_config in config["repositories"]:
        if repo_config["name"] == repo_name:
            return repo_config
    return None


def get_repo_config_by_url(repo_url: str) -> Optional[dict]:
    for repo_config in config["repositories"]:
        if repo_config["url"] == repo_url:
            return repo_config
    return None


def job_status_to_string(job_status: V1JobStatus) -> str:
    if job_status.active > 0:
        status = "Running"
    elif job_status.failed > 0:
        status = "Failed"
    elif job_status.succeeded > 0:
        status = "Completed"
    else:
        status = "Unknown"
    return status


def timedelta_to_string(timedelta: datetime.timedelta) -> str:
    """
    Returns a duration string for the given timedelta, with a resolution in seconds
    """
    parts = {"days": timedelta.days}
    parts["hours"], remainder = divmod(timedelta.seconds, 3600)
    parts["minutes"], parts["seconds"] = divmod(remainder, 60)

    def lex(duration_word, duration):
        if duration == 1:
            return f"{duration} {duration_word[:-1]}"
        else:
            return f"{duration} {duration_word}"

    delta_string = " ".join([lex(word, number) for word, number in parts.items() if number > 0])
    return delta_string if len(delta_string) > 0 else "seconds"
