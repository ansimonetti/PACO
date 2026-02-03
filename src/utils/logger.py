import logging
import os
from .env import LOG_TO_FILE, LOG_PATH


def setup_logger(name: str, to_file: bool = False, filename: str = "logs/paco.log", level: str = "INFO") -> logging.Logger:
	logger = logging.getLogger(name)

	if logger.handlers:
		return logger  # Non aggiungere più handler se già configurato

	logger.setLevel(level.upper())

	formatter = logging.Formatter('[%(asctime)s] - %(message)s')

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)
	logger.addHandler(console_handler)

	if to_file:
		log_dir = os.path.dirname(filename)
		if log_dir and not os.path.exists(log_dir):
			os.makedirs(log_dir, exist_ok=True)

		file_handler = logging.FileHandler(filename)
		file_handler.setFormatter(formatter)
		logger.addHandler(file_handler)

	return logger


def log_output(pipe, level, label):
    for line in pipe:
        logger.log(level, f"[{label}] {line.strip()}")

logger = setup_logger("__main__", to_file=LOG_TO_FILE, filename=LOG_PATH)
