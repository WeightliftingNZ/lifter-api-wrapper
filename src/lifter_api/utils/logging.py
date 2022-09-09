"""Logger for the project."""

import logging

from rich.logging import RichHandler

FORMAT = "%(message)s"
LEVEL = "DEBUG"
DATEFMT = "[%X]"

logging.basicConfig(
    level=LEVEL, format=FORMAT, datefmt=DATEFMT, handlers=[RichHandler()]
)
log = logging.getLogger("rich")
