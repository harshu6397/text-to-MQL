import logging
from colorlog import ColoredFormatter


class Logger:
    """
    A generic and flexible logger with colorized output and convenience methods.
    """

    def __init__(
        self,
        name="DefaultLogger",
        level=logging.INFO,
        log_format=None,
        name_color="green",
        asctime_color="blue",
        levelname_color="red",
        message_color="reset",
    ):
        """
        Initialize the logger instance.

        Args:
            name (str): The name of the logger.
            level (int): The logging level (e.g., DEBUG, INFO, WARNING).
            log_format (str): Custom log format string. Defaults to None.
            name_color (str): Color for the logger name.
            asctime_color (str): Color for the timestamp.
            levelname_color (str): Color for the log level name.
            message_color (str): Color for the log message.
        """
        self.name = name
        self.level = level
        self.log_format = log_format or self._default_log_format(
            name_color, asctime_color, levelname_color, message_color
        )
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        self._setup_logger()

    @staticmethod
    def _default_log_format(name_color, asctime_color, levelname_color, message_color):
        """
        Generates a default log format string using specified colors.

        Args:
            name_color (str): Color for the logger name.
            asctime_color (str): Color for the timestamp.
            levelname_color (str): Color for the log level name.
            message_color (str): Color for the log message.

        Returns:
            str: A formatted string with placeholders for colored output.
        """
        return (
            f"%({name_color})s%(name)s%(reset)s | "
            f"%({asctime_color})s%(asctime)s%(reset)s |     "
            f"%({levelname_color})s%(levelname)-8s%(reset)s | "
            f"%({message_color})s%(message)s%(reset)s"
        )

    def _setup_logger(self):
        """
        Sets up the logger with a colored formatter and stream handler.
        """
        formatter = ColoredFormatter(self.log_format)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(formatter)

        # Avoid adding duplicate handlers
        if not any(isinstance(handler, logging.StreamHandler) for handler in self.logger.handlers):
            self.logger.addHandler(stream_handler)

    # Convenience methods for logging
    def debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)

    def info(self, message):
        """Log an informational message."""
        self.logger.info(message)

    def warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message):
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message):
        """Log a critical message."""
        self.logger.critical(message)


# Instantiate the logger with desired configuration
logger = Logger(name="Text-to-MQL System", level=logging.DEBUG)
