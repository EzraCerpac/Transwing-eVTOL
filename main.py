import logging

from utility.logging.log_setup import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


def main():
    logger.info("Hello World!")
    logger.debug("Debugging")
    logger.warning("Warning")
    logger.error("Error")
    logger.critical("Critical")


if __name__ == '__main__':
    main()
