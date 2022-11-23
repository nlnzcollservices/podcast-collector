try:
	from settings import logging
except:
	from settings_prod import logging



logging.getLogger('dev')
logging.debug("This is a debug message")
logging.info("This is an info message")

# print(logger.debug("info"))
#logging.getLogger(__name__).addHandler(logging.NullHandler())