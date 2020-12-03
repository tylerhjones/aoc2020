def setup_custom_logger(name):
  import sys
  import logging
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(
    logging.Formatter(fmt='%(message)s'))
  log = logging.getLogger(name)
  log.propagate = False
  log.setLevel(logging.DEBUG)
  log.addHandler(handler)
  return log