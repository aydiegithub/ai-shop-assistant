import os
import logging as py_logging
from datetime import datetime

class logging:
    def __init__(self, log_dir='logs'):
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.log_dir = os.path.join(root_dir, log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        log_filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.log')
        log_path = os.path.join(self.log_dir, log_filename)

        self.logger = py_logging.getLogger('custom_logger')
        self.logger.setLevel(py_logging.INFO)
        formatter = py_logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = py_logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)