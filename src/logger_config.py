import logging
from pathlib import Path
import os
import json

# ---------------- Project paths ----------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
config_path = os.path.join(PROJECT_ROOT, "config", "config.json")
with open(config_path, "r") as f:
    config = json.load(f)

log_file = os.path.join(PROJECT_ROOT, config["output"]["log_file_path"])
log_folder_path = os.path.dirname(log_file)

# ---------------- Logger Setup ----------------
logger = logging.getLogger("SignalSimLogger")
logger.setLevel(logging.DEBUG)  # master level

if not logger.handlers:
    # Console handler (only WARNING+ if you want to keep it clean)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)  # show INFO+ on console

    # File handler (keep everything INFO+)
    os.makedirs(log_folder_path, exist_ok=True)
    fh = logging.FileHandler(log_file, mode="w")
    fh.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers
    logger.addHandler(ch)
    logger.addHandler(fh)

# ---------------- Blank line helper ----------------
def log_blank_line():
    for handler in logger.handlers:
        handler.stream.write("\n")
        handler.flush()

# ---------------- One-time log helper ----------------
_logged_once = set()  # track already logged messages

def log_once(message, level=logging.INFO):
    """Logs a message only once (never repeats in console or file)."""
    if message not in _logged_once:
        logger.log(level, message)
        _logged_once.add(message)



# import logging
# from pathlib import Path
# import os
# import json


# PROJECT_ROOT = Path(__file__).resolve().parent.parent
# config_path = os.path.join(PROJECT_ROOT,"config","config.json")
# with open(config_path, "r") as f:
#         config = json.load(f)
# log_file = os.path.join(PROJECT_ROOT,config["output"]["log_file_path"])
# log_folder_path = os.path.dirname(log_file)

# # Create a logger object
# logger = logging.getLogger("SignalSimLogger")
# logger.setLevel(logging.INFO)

# # Prevent adding multiple handlers if imported multiple times
# if not logger.handlers:
#     # Console handler
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.INFO)

#     # File handler
#     os.makedirs(log_folder_path, exist_ok=True)  # create logs folder if missing
#     fh = logging.FileHandler(log_file, mode="w")
#     fh.setLevel(logging.INFO)

#     # Formatter
#     formatter = logging.Formatter("%(asctime)s - %(message)s")
#     ch.setFormatter(formatter)
#     fh.setFormatter(formatter)

#     # Add handlers
#     logger.addHandler(ch)
#     logger.addHandler(fh)


# def log_blank_line():
#     for handler in logger.handlers:
#         handler.stream.write("\n")
#         handler.flush()
