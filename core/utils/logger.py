import datetime
import sys
import os
import logging


class GlobalLogger:
    def __init__(self):
        self.file_name = f"./logs/{str(datetime.datetime.now())[:-7]}.log"
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.format_string = "%(asctime)s | %(levelname)s | %(message)s"
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger("MultiOutputLogger")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.format_string, datefmt='%Y-%m-%d %H:%M:%S')

        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        file_handler = logging.FileHandler(self.file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(self.original_stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def __enter__(self):
        sys.stdout = self.StreamToLogger(self.logger, "stdout")
        sys.stderr = self.StreamToLogger(self.logger, "stderr")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)

    class StreamToLogger:
        def __init__(self, logger, stream_name):
            self.logger = logger
            self.stream_name = stream_name

        def write(self, message):
            if message.strip():
                self.logger.info(message.strip())

        def flush(self):
            pass
