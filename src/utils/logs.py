import os
import yaml
import logging
import logging.config
from pathlib import Path

def setup_logging(logger_name, config_path=os.path.join(os.path.dirname(__file__),'logs_conf.yaml')):

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        logging.config.dictConfig(config)
    return logging.getLogger(logger_name)