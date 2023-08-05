import logging
import logging.config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s - %(funcName)s() - %(filename)s:%(lineno)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)