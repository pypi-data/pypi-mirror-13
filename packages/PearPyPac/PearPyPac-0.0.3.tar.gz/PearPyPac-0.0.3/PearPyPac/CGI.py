# -*- coding: utf-8 -*-

import os
import cgi
import json


class PearCGI:
    def __init__(self):
        return

    def checkPOSTMethod(self):
        if(os.environ["REQUEST_METHOD"] == "POST"):
            return True
        else:
            return False

    def checkGETMethod(self):
        if(os.environ["REQUEST_METHOD"] == "GET"):
            return True
        else:
            return False

    def getParameter(self):
        parameter = cgi.FieldStorage()
        return parameter

    def jsonEncode(self, data):
            results = json.dumps(data, indent=4)
            return results
