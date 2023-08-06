# -*- coding: utf-8 -*-

"""
   BatchlyApi.Controllers.ProcessorsController

   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
import unirest

from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Configuration import Configuration
from BatchlyApi.APIException import APIException
from BatchlyApi.Models.ProcessorModel import ProcessorModel
from BatchlyApi.Models.ProcessorModel import ProcessorModel
from BatchlyApi.Models.DescribeParameterGroupResponse import DescribeParameterGroupResponse
from BatchlyApi.Models.DescribeParameterGroupResponse import DescribeParameterGroupResponse
from BatchlyApi.Models.ProcessorModel import ProcessorModel
from BatchlyApi.Models.ProcessorModel import ProcessorModel
from BatchlyApi.CustomAuthUtility import CustomAuthUtility

class ProcessorsController(object):


    """A Controller to access Endpoints in the BatchlyApi API."""

    def list_marketplace_processors(self):
        """Does a GET request to /api/Processors/Marketplace.

        TODO: type endpoint description here.

        Returns:
            list of ProcessorModel: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Processors/Marketplace"

        # Validate and preprocess url
        query_url = APIHelper.clean_url(query_builder)

        # Prepare headers
        headers = {

            "user-agent": "batchly/0.7.1",
            "accept": "application/json",

        }

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(query_url, 'GET', headers)

        # Prepare and invoke the API call request to fetch the response
        response = unirest.get(query_url, headers=headers)

        # Error handling using HTTP status codes
        if response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body) 
    
        #try to cast response to list of desired type
        if isinstance(response.body, list):
            # Response is already in a list, return the list of objects 
            value = list()
            for item in response.body:
                try:
                    value.append(ProcessorModel(**item))
                except TypeError:
                    raise APIException("Invalid JSON returned", response.code, response.body)
                    
            return value
        
        # If we got here then an error occured while trying to parse the response
        raise APIException("Invalid JSON returned", response.code, response.body)

    def list_vault_processors(self,
                              account_id):
        """Does a GET request to /api/Processors/Vault/{accountId}.

        TODO: type endpoint description here.

        Args:
            account_id (string): TODO: type description here.

        Returns:
            list of ProcessorModel: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Processors/Vault/{accountId}"

        # Process optional template parameters
        query_builder = APIHelper.append_url_with_template_parameters(query_builder, { 
            "accountId": account_id
        })

        # Validate and preprocess url
        query_url = APIHelper.clean_url(query_builder)

        # Prepare headers
        headers = {

            "user-agent": "batchly/0.7.1",
            "accept": "application/json",

        }

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(query_url, 'GET', headers)

        # Prepare and invoke the API call request to fetch the response
        response = unirest.get(query_url, headers=headers)

        # Error handling using HTTP status codes
        if response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body) 
    
        #try to cast response to list of desired type
        if isinstance(response.body, list):
            # Response is already in a list, return the list of objects 
            value = list()
            for item in response.body:
                try:
                    value.append(ProcessorModel(**item))
                except TypeError:
                    raise APIException("Invalid JSON returned", response.code, response.body)
                    
            return value
        
        # If we got here then an error occured while trying to parse the response
        raise APIException("Invalid JSON returned", response.code, response.body)

    def add_parameter_group(self,
                            processor_id,
                            request):
        """Does a POST request to /api/Processors/{processorId}/ParameterGroups.

        TODO: type endpoint description here.

        Args:
            processor_id (string): TODO: type description here.
            request (AddParameterGroupRequest): TODO: type description here.

        Returns:
            DescribeParameterGroupResponse: Response from the API. Created

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Processors/{processorId}/ParameterGroups"

        # Process optional template parameters
        query_builder = APIHelper.append_url_with_template_parameters(query_builder, { 
            "processorId": processor_id
        })

        # Validate and preprocess url
        query_url = APIHelper.clean_url(query_builder)

        # Prepare headers
        headers = {

            "user-agent": "batchly/0.7.1",
            "accept": "application/json",
            "content-type": "application/json; charset=utf-8",

        }

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(query_url, 'POST', headers)

        # Prepare and invoke the API call request to fetch the response
        response = unirest.post(query_url, headers=headers,  params=APIHelper.json_serialize(request))

        # Error handling using HTTP status codes
        if response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body) 
    
        # Try to cast response to desired type
        if isinstance(response.body, dict):
            # Response is already in a dictionary, return the object 
            try:
                return DescribeParameterGroupResponse(**response.body)
            except TypeError:
                raise APIException("Invalid JSON returned", response.code, response.body)
        
        # If we got here then an error occured while trying to parse the response
        raise APIException("Invalid JSON returned", response.code, response.body)

    def get_describe_parameter_group(self,
                                     parameter_group_id,
                                     processor_id):
        """Does a GET request to /api/Processors/{processorId}/ParameterGroups/{parameterGroupId}.

        TODO: type endpoint description here.

        Args:
            parameter_group_id (string): TODO: type description here.
            processor_id (string): TODO: type description here.

        Returns:
            DescribeParameterGroupResponse: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Processors/{processorId}/ParameterGroups/{parameterGroupId}"

        # Process optional template parameters
        query_builder = APIHelper.append_url_with_template_parameters(query_builder, { 
            "parameterGroupId": parameter_group_id,
            "processorId": processor_id
        })

        # Validate and preprocess url
        query_url = APIHelper.clean_url(query_builder)

        # Prepare headers
        headers = {

            "user-agent": "batchly/0.7.1",
            "accept": "application/json",

        }

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(query_url, 'GET', headers)

        # Prepare and invoke the API call request to fetch the response
        response = unirest.get(query_url, headers=headers)

        # Error handling using HTTP status codes
        if response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body) 
    
        # Try to cast response to desired type
        if isinstance(response.body, dict):
            # Response is already in a dictionary, return the object 
            try:
                return DescribeParameterGroupResponse(**response.body)
            except TypeError:
                raise APIException("Invalid JSON returned", response.code, response.body)
        
        # If we got here then an error occured while trying to parse the response
        raise APIException("Invalid JSON returned", response.code, response.body)

    def add_processor_to_vault(self,
                               request):
        """Does a POST request to /api/Processors/Vault.

        TODO: type endpoint description here.

        Args:
            request (AddProcessorRequest): TODO: type description here.

        Returns:
            ProcessorModel: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Processors/Vault"

        # Validate and preprocess url
        query_url = APIHelper.clean_url(query_builder)

        # Prepare headers
        headers = {

            "user-agent": "batchly/0.7.1",
            "accept": "application/json",
            "content-type": "application/json; charset=utf-8",

        }

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(query_url, 'POST', headers)

        # Prepare and invoke the API call request to fetch the response
        response = unirest.post(query_url, headers=headers,  params=APIHelper.json_serialize(request))

        # Error handling using HTTP status codes
        if response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body) 
    
        # Try to cast response to desired type
        if isinstance(response.body, dict):
            # Response is already in a dictionary, return the object 
            try:
                return ProcessorModel(**response.body)
            except TypeError:
                raise APIException("Invalid JSON returned", response.code, response.body)
        
        # If we got here then an error occured while trying to parse the response
        raise APIException("Invalid JSON returned", response.code, response.body)

    def upload_file(self,
                    accountid,
                    file):
        """Does a POST request to /api/Processors/Upload.

        TODO: type endpoint description here.

        Args:
            accountid (string): TODO: type description here.
            file (string): File Contents

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
        query_builder += "/api/Processors/Upload"

        # Process optional query parameters
        query_parameters = {
            "accountid": accountid
        }
        query_builder = APIHelper.append_url_with_query_parameters(query_builder, query_parameters)

        # Validate and preprocess url
        query_url = APIHelper.clean_url(query_builder)

        # Prepare headers
        headers = {

            "user-agent": "batchly/0.7.1",

        }

        # Prepare parameters
        parameters = {
            "file":  open(file, mode="r") if file is not None else None
        }
        # Send the form body as url encoded data
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        form_encoded_params = dict()
        for (key, value) in parameters.items():
            if isinstance(value, list):
                # Loop through each item in the list and add it by number
                i = 0
                for entry in value:
                    form_encoded_params.update(APIHelper.form_encode(entry, key + "[" + str(i) + "]"))
                    i += 1
            elif isinstance(value, dict):
                # Loop through each item in the dictionary and add it
                form_encoded_params.update(APIHelper.form_encode(value, key))
            else:
                # Add the current item
                form_encoded_params[key] = value
        
        parameters = ''
        for (key, value) in form_encoded_params.items():
            separator = '&' if len(parameters) > 0 else '' 
            parameters = parameters + '{0}{1}={2}'.format(separator, key, value)

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(query_url, 'POST', headers)

        # Prepare and invoke the API call request to fetch the response
        response = unirest.post(query_url, headers=headers, params=parameters)

        # Error handling using HTTP status codes
        if response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body) 
    
        return response.body

    def add_processor_to_job(self,
                             request):
        """Does a POST request to /api/Processors.

        TODO: type endpoint description here.

        Args:
            request (AddProcessorRequest): TODO: type description here.

        Returns:
            ProcessorModel: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Processors"

        # Validate and preprocess url
        query_url = APIHelper.clean_url(query_builder)

        # Prepare headers
        headers = {

            "user-agent": "batchly/0.7.1",
            "accept": "application/json",
            "content-type": "application/json; charset=utf-8",

        }

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(query_url, 'POST', headers)

        # Prepare and invoke the API call request to fetch the response
        response = unirest.post(query_url, headers=headers,  params=APIHelper.json_serialize(request))

        # Error handling using HTTP status codes
        if response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body) 
    
        # Try to cast response to desired type
        if isinstance(response.body, dict):
            # Response is already in a dictionary, return the object 
            try:
                return ProcessorModel(**response.body)
            except TypeError:
                raise APIException("Invalid JSON returned", response.code, response.body)
        
        # If we got here then an error occured while trying to parse the response
        raise APIException("Invalid JSON returned", response.code, response.body)
