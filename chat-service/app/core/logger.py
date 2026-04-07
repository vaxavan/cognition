import logging, sys
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
logger = logging.getLogger("chat-service")
