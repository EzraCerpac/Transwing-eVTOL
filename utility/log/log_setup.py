import atexit
import json
import logging.config
import logging.handlers
import pathlib


def setup_logging():
    config_file = pathlib.Path(__file__).resolve().parent / 'config.json'
    with open(config_file) as f_in:
        config = json.load(f_in)

    log_file_path = pathlib.Path(config['handlers']['file']['filename'])
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(config)
