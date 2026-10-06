import logging
import sys

from loguru import logger

from delivery.config import settings


class InterceptHandler(logging.Handler):
    """Перехватывает стандартный logging → loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore[assignment]
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging() -> None:
    """Настроить loguru + перехватить логи uvicorn, sqlalchemy, fastapi."""
    level = settings.app.log_level.upper()
    debug = settings.app.debug

    logger.remove()

    if debug:
        fmt = (
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{message}</cyan> {extra}"
        )
        logger.add(
            sys.stdout,
            level=level,
            colorize=True,
            format=fmt,
            backtrace=True,
            diagnose=True,
        )
    else:
        logger.add(
            sys.stdout,
            level=level,
            serialize=True,
            enqueue=True,
            backtrace=False,
            diagnose=False,
        )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy.engine",
        "alembic",
    ):
        lib_logger = logging.getLogger(name)
        lib_logger.handlers = [InterceptHandler()]
        lib_logger.propagate = False

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
