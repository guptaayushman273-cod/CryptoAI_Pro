import logging
import os
import sys


# ==========================================
# LOG FOLDER
# ==========================================

LOG_FOLDER = "logs"

os.makedirs(LOG_FOLDER, exist_ok=True)


# ==========================================
# LOG FILE
# ==========================================

LOG_FILE = os.path.join(
    LOG_FOLDER,
    "cryptoai.log"
)


# ==========================================
# LOGGER SETUP
# ==========================================

def setup_logger():

    logger = logging.getLogger("CryptoAI")

    logger.setLevel(logging.INFO)

    # Prevent messages from being sent
    # to the root logger as well.
    logger.propagate = False

    # Avoid creating duplicate handlers
    # if setup_logger() is called more than once.
    if logger.handlers:
        return logger

    # ------------------------------------------
    # Enable UTF-8 in the Windows console
    # ------------------------------------------

    try:
        sys.stdout.reconfigure(
            encoding="utf-8",
            errors="replace"
        )

        sys.stderr.reconfigure(
            encoding="utf-8",
            errors="replace"
        )

    except AttributeError:
        pass

    # ==========================================
    # FORMAT
    # ==========================================

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # ==========================================
    # FILE HANDLER
    # ==========================================

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # ==========================================
    # CONSOLE HANDLER
    # ==========================================

    console_handler = logging.StreamHandler(
        sys.stdout
    )

    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # ==========================================
    # ADD HANDLERS
    # ==========================================

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger