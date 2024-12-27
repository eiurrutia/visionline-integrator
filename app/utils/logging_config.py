import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

sys.stdout.reconfigure(line_buffering=True)

logging.getLogger("apscheduler").setLevel(logging.INFO)