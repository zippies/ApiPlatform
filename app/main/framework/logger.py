# -*- coding: utf-8 -*-
import logging,os
from config import Config

class Logger(object):
    def __init__(self,name):
        self.format = '%(message)s'
        fm = logging.Formatter(self.format)
        logging.basicConfig(
            level=logging.DEBUG,
            format=self.format,
            datefmt='%Y_%m_%d %H:%M:%S',
            filename="tmp",
            filemode='w'
        )
        if not os.path.isdir(os.path.join(Config.log_path,name[:name.rindex("/")])):
            os.makedirs(os.path.join(Config.log_path,name[:name.rindex("/")]))

        infohandler = logging.FileHandler('%s.log' % os.path.join(Config.log_path,name))

        infohandler.setLevel(logging.INFO)
        infohandler.setFormatter(fm)
        self.infologger = logging.getLogger('%slogger' % name)
        self.infologger.addHandler(infohandler)

    def log(self, msg):
        self.infologger.info(msg)