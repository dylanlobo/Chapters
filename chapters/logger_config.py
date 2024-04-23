import json
import pathlib
import logging.config

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


config_filename = "log_config.json"
config_file = pathlib.Path("./log_config.json")
if config_file.is_file():
    with open(config_file) as cfg_file:
        config = json.load(cfg_file)
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
                "filters": ["no_errors"],
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "stream": "ext://sys.stderr",
                "level": "WARNING",
            },
        },
        "loggers": {"root": {"level": "INFO", "handlers": ["stdout", "stderr"]}},
    }

logging.config.dictConfig(config)

app_logger = logging.getLogger("chapters_logger")
if not config_file.exists():
    app_logger.warning(f"No log config file: {config_filename}")
    app_logger.info("Using statically defined log config")
    app_logger.info(config)
