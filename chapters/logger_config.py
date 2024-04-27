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


_cfg_filename = "log_config.json"
_cfg_file = pathlib.Path(f"./{_cfg_filename}")

_config_loading_exception = None


def _get_logging_config() -> Dict:
    """Setup the logger configuration.
    Note: Errors/Exceptions that are encountered during logger configuration
    setup are cached in the global variable 'config_loading_exception'
    and displayed after the logger has been successfully configured.
    """
    try:
        with open(_cfg_file) as cfg_f:
            config = json.load(cfg_f)
    except Exception as e:
        global _config_loading_exception
        _config_loading_exception = e
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


def _log_config_loading_exceptions():
    if type(_config_loading_exception) is FileNotFoundError:
        _app_logger.debug(
            f"Logger config file {_cfg_filename} not found in current working directory."
        )
    else:
        _app_logger.debug("Error encountered when loading logger config file.")
        _app_logger.debug(_config_loading_exception)
    _app_logger.debug("Falling back to statically defined log config")
    _app_logger.debug(logging_config)


if _config_loading_exception is not None:
    _log_config_loading_exceptions()


def logger():
    return _app_logger
