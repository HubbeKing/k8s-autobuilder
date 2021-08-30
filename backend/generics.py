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
    with open(config_path) as config_file:
        # load file with full YAML language, we can assume config file is trusted input, since it's up to the user to create it
        config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
    return config
