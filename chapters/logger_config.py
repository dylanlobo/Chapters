import json
import pathlib
import logging.config
from typing import Dict

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


cfg_filename = "log_config.json"
cfg_file = pathlib.Path(f"./{cfg_filename}")


def _get_logging_config() -> Dict:
    if cfg_file.is_file():
        with open(cfg_file) as cfg_f:
            config = json.load(cfg_f)
    else:
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {
                    "format": "%(levelname)s: %(filename)s(%(lineno)s): %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S%z",
                }
            },
            "filters": {
                "no_errors": {"()": "chapters.log_filters.NonErrorFilter"},
                "errors": {"()": "chapters.log_filters.ErrorFilter"},
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout",
                    "level": "INFO",
                    "filters": ["no_errors"],
                },
                "stderr": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple",
                    "stream": "ext://sys.stderr",
                    "level": "WARNING",
                },
            },
            "loggers": {"root": {"level": "DEBUG", "handlers": ["stdout", "stderr"]}},
        }
    return config


logging_config = _get_logging_config()
logging.config.dictConfig(logging_config)
_app_logger = logging.getLogger("chapters_logger")

config_checked = False


def _config_loading_check():
    global config_checked
    if not cfg_file.exists() and not config_checked:
        _app_logger.info(
            f"Logger config file {cfg_filename} not found in current working directory."
        )
        _app_logger.info("Using statically defined log config")
        _app_logger.debug(logging_config)
    config_checked = True


def logger():
    _config_loading_check()
    return _app_logger
