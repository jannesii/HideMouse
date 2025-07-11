import functools
import logging


def handle_errors(func):
    # grab the logger whose name == the module where func was defined
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # use that module logger instead of the root logger
            logger.exception(f"Error in {func.__name__}: {e}", exc_info=True)
            # logger.info(f"Error in {func.__name__}: {e}")
    return wrapper
