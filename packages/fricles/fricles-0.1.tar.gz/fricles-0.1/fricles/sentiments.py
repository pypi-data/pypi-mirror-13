""" Module provides sentiment for the given text.

        >> How to install ?
            pip install fricles

        >> How to use ?
            from fricles import sentiments
        sent_op = sentiments().get_sentiments("api_key", "text")
@author: Chetan G
@contact: chetan.ganjihal@gmail.com
@since: Created on 2016-02-04
@copyright: Copyright (C) 2016 Chetan Team. All rights reserved.
@license: http://www.apache.org/licenses/LICENSE-2.0 Apache License
"""

#'

import urllib2
import urllib
import json
import copy

class sentiments:

    FRICLE_URL = "http://fricles.com:8080/fricles/api/v1/get_sentiments"
    INPUT_TPL = { "inputs" : {"api_key" :  "46:3a:bf:30:42:03:5d:83:e1:21:28:32:f6:f0:38:39",  "text" :""} }

    def get_sentiments(self, api_key, text):
        inputData = copy.deepcopy(self.INPUT_TPL.copy())
        inputData["inputs"]["text"] = text
        inputData["inputs"]["api_key"] = api_key
        params = urllib.urlencode(inputData)
        request = urllib2.Request(self.FRICLE_URL, data=inputData, headers={ 'Content-Type':'application/json' })
        try:
            response = urllib2.urlopen(request).read()
            return json.loads(response)
        except urllib2.HTTPError, err:
            return {"status": "FAILED","http_code" : err.code, "message" : err.message}
        except urllib2.URLError, err:
            return {"status": "FAILED","http_code" : err.errno, "message" : err.reason}
        except Exception as excep:
            return {"status" : "ERROR", "http_code": -1, "message": excep.message}
