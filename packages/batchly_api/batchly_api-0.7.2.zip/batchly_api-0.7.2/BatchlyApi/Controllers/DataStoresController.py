# -*- coding: utf-8 -*-

"""
   BatchlyApi.Controllers.DataStoresController

   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
import unirest

from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Configuration import Configuration
from BatchlyApi.APIException import APIException
from BatchlyApi.CustomAuthUtility import CustomAuthUtility

class DataStoresController(object):


    """A Controller to access Endpoints in the BatchlyApi API."""

    def add_s_3(self,
                model):
        """Does a POST request to /api/DataStores/S3.

        TODO: type endpoint description here.

        Args:
            model (AddS3DataStoreRequest): TODO: type description here.

        Returns:
            string: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/DataStores/S3"

        # Validate and preprocess url
        query_url = APIHelper.clean_url(query_builder)

        # Prepare headers
        headers = {

            "user-agent": "batchly/0.7.1",
            "content-type": "application/json; charset=utf-8",

        }

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(query_url, 'POST', headers)

        # Prepare and invoke the API call request to fetch the response
        response = unirest.post(query_url, headers=headers,  params=APIHelper.json_serialize(model))

        # Error handling using HTTP status codes
        if response.code == 400:
            raise APIException("BadRequest", 400, response.body)

        elif response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body)
        
        return response.body
