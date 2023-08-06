import loggers

def set_logging(level=loggers.INFO):
    loggers.basicConfig(level=loggers.WARN, format='%(message)s')
    loggers.getLogger('boto').setLevel(loggers.INFO)

    SG_LOGGER = loggers.getLogger()
    SG_LOGGER.setLevel(loggers.INFO)
    sg_handler = loggers.FileHandler('ec2ls.log')
    sg_handler.setFormatter(loggers.Formatter('%(asctime)-15s %(levelname)s %(module)s %(lineno)d: %(message)s'))
    SG_LOGGER.addHandler(sg_handler)

