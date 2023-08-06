__author__ = 'dcortes'

import requests


class HttpManagement():

    @staticmethod
    def post(endpoint, url, response="json", headers=None, data=None, jsonData=None):
        url = endpoint + url
        try:
            req = requests.post(url, headers=headers, timeout=10, verify=True, data=data, json=jsonData)
            if req.status_code in range(200, 299):
                return req.json() if response == "json" else req.content
            else:
                raise Exception(u"dexma_drivers - http_management - code {} with message {}".format(req.status_code, req.json()))
        except Exception as e:
            raise Exception(u"dexma_drivers - http_management - {}".format(e.message))

    @staticmethod
    def put(endpoint, url, response="json", headers=None, data=None, jsonData=None):
        url = endpoint + url
        try:
            req = requests.put(url, headers=headers, timeout=10, verify=True, data=data, json=jsonData)
            if req.status_code in range(200, 299):
                return req.json() if response == "json" else req.content
            else:
                raise Exception(u"dexma_drivers - http_management - code {} with message {}".format(req.status_code, req.json()))
        except Exception as e:
            raise Exception(u"dexma_drivers - http_management - {}".format(e.message))

    @staticmethod
    def get(endpoint, url, response="json", headers=None, params=None):
        url = endpoint + url
        try:
            req = requests.get(url, params=params, headers=headers, timeout=10, verify=True)
            if req.status_code in range(200, 299):
                return req.json() if response == "json" else req.content
            else:
                raise Exception(u"dexma_drivers - http_management - code {} with message {}".format(req.status_code, req.json()))
        except Exception as e:
            raise Exception(u"dexma_drivers - http_management - {}".format(e.message))

    @staticmethod
    def delete(endpoint, url, response="json", headers=None, data=None, jsonData=None):
        url = endpoint + url
        try:
            req = requests.delete(url, headers=headers, timeout=10, verify=True, data=data, json=jsonData)
            if req.status_code in range(200, 299):
                return req.json() if response == "json" else req.content
            else:
                raise Exception(u"dexma_drivers - http_management - code {} with message {}".format(req.status_code, req.json()))
        except Exception as e:
            raise Exception(u"dexma_drivers - http_management - {}".format(e.message))