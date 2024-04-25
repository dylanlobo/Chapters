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

config_loading_exception = None


def _get_logging_config() -> Dict:
    try:
        with open(cfg_file) as cfg_f:
            config = json.load(cfg_f)
    except Exception as e:
        global config_loading_exception
        config_loading_exception = e
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
    if not config_checked and config_loading_exception is not None:
        if type(config_loading_exception) is FileNotFoundError:
            _app_logger.info(
                f"Logger config file {cfg_filename} not found in current working directory."
            )
        else:
            _app_logger.error("Error encountered when loading logger config file.")
            _app_logger.error(config_loading_exception)
            _app_logger.info("Falling back to statically defined log config")
            _app_logger.debug(logging_config)
    config_checked = True


def logger():
    _config_loading_check()
    return _app_logger
