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
