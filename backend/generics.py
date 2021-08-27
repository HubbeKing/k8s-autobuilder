import logging
import os
import sys
import yaml


def setup_logging(logger_name):
    root_logger = logging.getLogger()
    if int(os.environ.get("FLASK_DEBUG", 0)) == 1:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%H:%M:%S'))
    root_logger.addHandler(stream_handler)

    return logging.getLogger(logger_name)


def load_config(config_path: str) -> dict:
    config = yaml.load(config_path)
    return config
