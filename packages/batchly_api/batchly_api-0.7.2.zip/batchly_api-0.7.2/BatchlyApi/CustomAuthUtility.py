# -*- coding: utf-8 -*-

'''
 BatchlyApi

 This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
'''
import unirest
import hmac
import hashlib
import base64
import uuid
import ast
import urllib
import time
from Configuration import *
from urlparse import urlparse

class CustomAuthUtility:

    @staticmethod
    def query_string(parameters):
        return urllib.quote_plus(urllib.urlencode(sorted(parameters.items())))

    @staticmethod
    def percent_encode(value):
        return urllib.quote(value, safe='')

    @staticmethod
    def appendCustomAuthParams(url, method, headers):
        '''
        Appends the necessary OAuth credentials for making this authorized call

        :param url: resource location
		:type url: str
		:param method: request method type
		:type method: str
        :param headers: The out going request to access the resource
		:type headers: dict
        '''
    
        HEADER_AUTHORIZATION = "Authorization"
        HMAC_TEMPLATE = "Hmac {0}"
        HEADER_NONCE = "Nonce"
        HEADER_TIMESTAMP = "Timestamp"
        HEADER_API_KEY = "Api-Key"
    
        parsed_url = urlparse(url)
        apiKey = Configuration.API_KEY
        apiSecret = Configuration.API_SECRET

        req_url = parsed_url.geturl()

        if (parsed_url.port == 80 or parsed_url.port == 443 or parsed_url.port == None):
            req_url = parsed_url.scheme + '://' + parsed_url.hostname + parsed_url.path
        else:
            req_url = parsed_url.scheme + '://' + parsed_url.hostname + ":" + str(parsed_url.port) + parsed_url.path

        hmacHeaders = {
        HEADER_NONCE: uuid.uuid4().get_hex(),
        HEADER_TIMESTAMP: int(time.time()),
        HEADER_API_KEY: apiKey
        }

        params = hmacHeaders.copy()
        method = method.upper()

        if parsed_url.query != '':
            params.update(ast.literal_eval(parsed_url.query))

        base_str = '&'.join([method.upper(), CustomAuthUtility.percent_encode(req_url), CustomAuthUtility.query_string(params)])

        key = CustomAuthUtility.percent_encode(apiSecret)

        digest = hmac.new(key, base_str, hashlib.sha1).digest()

        headers[HEADER_AUTHORIZATION] = str.format( HMAC_TEMPLATE , CustomAuthUtility.percent_encode(base64.b64encode(digest).decode()) )
        headers[HEADER_NONCE] = hmacHeaders[HEADER_NONCE]
        headers[HEADER_TIMESTAMP] = hmacHeaders[HEADER_TIMESTAMP]
        headers[HEADER_API_KEY] = hmacHeaders[HEADER_API_KEY]
