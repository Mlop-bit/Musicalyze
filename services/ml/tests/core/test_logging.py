import logging
from collections.abc import Iterator

import pytest

from ml.core.logging import PACKAGE_LOGGER_NAME, configure_logging


@pytest.fixture(autouse=True)
def restore_package_logger() -> Iterator[None]:
    package_logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    handlers = list(package_logger.handlers)
    level = package_logger.level
    propagate = package_logger.propagate
    package_logger.handlers.clear()
    yield
    package_logger.handlers[:] = handlers
    package_logger.setLevel(level)
    package_logger.propagate = propagate


def test_configure_logging_sets_level_on_the_package_logger_only() -> None:
    root_level = logging.getLogger().level

    configure_logging(logging.DEBUG)

    assert logging.getLogger(PACKAGE_LOGGER_NAME).level == logging.DEBUG
    assert logging.getLogger().level == root_level


def test_configure_logging_is_idempotent() -> None:
    configure_logging()
    configure_logging()

    assert len(logging.getLogger(PACKAGE_LOGGER_NAME).handlers) == 1


def test_info_messages_from_package_modules_are_emitted(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging()

    logging.getLogger("ml.training.loader").info("batch uploaded")

    assert "batch uploaded" in capsys.readouterr().err
