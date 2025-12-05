# app/logging_conf.py
import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """
    Prosta konfiguracja logowania dla całej aplikacji.
    Logi lecą na stdout i mają format:
    2025-01-01 12:00:00 [INFO] app.module: wiadomość
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
