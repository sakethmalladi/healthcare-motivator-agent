import logging
from src.config.settings import LOG_LEVEL

# Basic logging configuration for the project
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

