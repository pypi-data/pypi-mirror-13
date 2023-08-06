# -*- coding: utf-8 -*-

import ConfigParser


class PearConfig:
    def __init__(self, conf_path):
        """ initialize """
        self.settings = self.getConfig(conf_path)
    
    def getConfig(self, conf_path):
        """ set configure """
        conf = ConfigParser.SafeConfigParser()
        conf.read(conf_path)
        return conf
