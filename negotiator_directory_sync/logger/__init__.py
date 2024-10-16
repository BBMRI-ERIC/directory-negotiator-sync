import logging

logging.getLogger(__name__).addHandler(logging.StreamHandler())


def setup_logger(log_level=logging.INFO):
    """
    Set up a logger with a console handler and the given log level.
    """
    logger = logging.getLogger('directory-negotiator-sync')

    # Avoid adding multiple handlers if the logger is already configured
    if len(logger.handlers) == 0:
        logger.setLevel(log_level)

        # Create a console handler
        console_handler = logging.StreamHandler()

        # Set log format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(console_handler)

    return logger


LOG = setup_logger(logging.DEBUG)
