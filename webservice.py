from email import header
from requests.auth import HTTPBasicAuth  
import requests

zhouwei0115 = HTTPBasicAuth(username="winter.ou@sap.com", password="EmilyPrentiss1012")

auth = zhouwei0115
class WebService(object):
    def __init__(self, url, path, auth1=auth):
        self.__url__ = url
        self.auth = auth1
        self.headers = None
       # with open(path, 'r') as f:
       #     self.__payload__ = f.read()

    def setUrl(self, url):
        self.__url__ = url
    
    def setHeaders(self, headers):
        self.headers = headers
    
    def getHeaders(self):
        return self.headers

    def get(self, headers, payload=None):
        response = requests.get(self.__url__, data=payload, headers=headers, auth=self.auth)
        return response

    def post(self,headers, payload):
        try:
            response = requests.post(self.__url__,  headers=headers, json=payload, auth=self.auth, timeout=60000)
        except TypeError:
            response = requests.post(self.__url__,  headers=headers, data=payload, auth=self.auth, timeout=60000)
        
        return response

    def batch(self,headers, payload):
        try:
            response = requests.post(self.__url__,  headers=headers, data=payload, auth=self.auth, timeout=60000)
        except TypeError:
            response = requests.post(self.__url__,  headers=headers, json=payload, auth=self.auth, timeout=60000)
        
        return response

    def put(self,headers, payload):
        response = requests.put(self.__url__,  headers=headers, json=payload, auth=self.auth, timeout=60000)
        return response
