import logging

# Create singleton for api client logging
logger = logging.getLogger("predata_api_client")
logger.setLevel(logging.DEBUG)

# add std out stream handler
format_str = "[%(asctime)s] [%(levelname)s] %(message)s"
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt=format_str))
logger.addHandler(handler)

# mute requests logging
logging.getLogger("requests").setLevel(logging.WARNING)
