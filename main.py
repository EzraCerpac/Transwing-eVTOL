import logging

from utility.log import logger


def main():
    logger.info("Hello World!")
    logger.debug("Debugging")
    logger.warning("Warning")
    logger.error("Error")
    logger.critical("Critical")


if __name__ == '__main__':
    main()
