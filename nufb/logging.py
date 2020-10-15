import logging

from nufb.console import Foreground


def init_logging(level: int = logging.DEBUG, color: bool = True) -> None:
    if level <= logging.DEBUG:
        if color:
            fmt = (
                f"{Foreground.RED_BOLD}%(levelname)-7s "  # noqa: SC300
                f"{Foreground.YELLOW}%(pathname)s{Foreground.RESET}:"  # noqa: SC300
                f"{Foreground.YELLOW}%(lineno)d{Foreground.RESET} "  # noqa: SC300
                f"{Foreground.GREEN}%(funcName)s{Foreground.RESET} "  # noqa: SC300
                "%(message)s"
            )
        else:
            fmt = "%(levelname)-7s %(pathname)s:%(lineno)d:%(funcName)s %(message)s"  # noqa: SC300
    elif color:
        fmt = f"{Foreground.RED}%(levelname)7s{Foreground.RESET} %(message)s"  # noqa: SC300
    else:
        fmt = "%(levelname)7s %(message)s"  # noqa: SC300

    logging.basicConfig(level=level, format=fmt)


def get_logger(name: str) -> logging.Logger:
    """
    Create new logger.

    :param name: The logger domain.
    :return: New logger.
    """
    return logging.getLogger(name)
