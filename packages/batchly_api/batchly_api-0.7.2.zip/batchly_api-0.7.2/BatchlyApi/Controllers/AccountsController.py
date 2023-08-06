# -*- coding: utf-8 -*-

"""
   BatchlyApi.Controllers.AccountsController

   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
import unirest

from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Configuration import Configuration
from BatchlyApi.APIException import APIException
from BatchlyApi.Models.ProjectModel import ProjectModel
from BatchlyApi.Models.AccountModel import AccountModel
from BatchlyApi.Models.AccountModel import AccountModel
from BatchlyApi.CustomAuthUtility import CustomAuthUtility


class AccountsController(object):


    """A Controller to access Endpoints in the BatchlyApi API."""

    def list_projects(self,
                      id):
        """Does a GET request to /api/Accounts/{id}/Projects.

        TODO: type endpoint description here.

        Args:
            id (string): TODO: type description here.

        Returns:
            list of ProjectModel: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Accounts/{id}/Projects"

        # Process optional template parameters
        query_builder = APIHelper.append_url_with_template_parameters(query_builder, { 
            "id": id
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
                    value.append(ProjectModel(**item))
                except TypeError:
                    raise APIException("Invalid JSON returned", response.code, response.body)
                    
            return value
        
        # If we got here then an error occured while trying to parse the response
        raise APIException("Invalid JSON returned", response.code, response.body)

    def add_aws_cloud_account(self,
                              model):
        """Does a POST request to /api/Accounts/AWS.

        TODO: type endpoint description here.

        Args:
            model (AddAWSAccountRequest): TODO: type description here.

        Returns:
            AccountModel: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Accounts/AWS"

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
        response = unirest.post(query_url, headers=headers,  params=APIHelper.json_serialize(model))

        # Error handling using HTTP status codes
        if response.code == 400:
            raise APIException("BadRequest", 400, response.body)

        elif response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body)
        
        # Try to cast response to desired type
        if isinstance(response.body, dict):
            # Response is already in a dictionary, return the object 
            try:
                return AccountModel(**response.body)
            except TypeError:
                raise APIException("Invalid JSON returned", response.code, response.body)
        
        # If we got here then an error occured while trying to parse the response
        raise APIException("Invalid JSON returned", response.code, response.body)

    def list_accounts(self):
        """Does a GET request to /api/Accounts.

        TODO: type endpoint description here.

        Returns:
            list of AccountModel: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Accounts"

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
                    value.append(AccountModel(**item))
                except TypeError:
                    raise APIException("Invalid JSON returned", response.code, response.body)
                    
            return value
        
        # If we got here then an error occured while trying to parse the response
        raise APIException("Invalid JSON returned", response.code, response.body)

    def delete(self,
               id):
        """Does a DELETE request to /api/Accounts/{id}.

        TODO: type endpoint description here.

        Args:
            id (string): TODO: type description here.

        Returns:
            void: Response from the API. OK

        Raises:
            APIException: When an error occurs while fetching the data from
                the remote API. This exception includes the HTTP Response
                code, an error message, and the HTTP body that was received in
                the request.

        """
        # The base uri for api requests
        query_builder = Configuration.BASE_URI
 
        # Prepare query string for API call
        query_builder += "/api/Accounts/{id}"

        # Process optional template parameters
        query_builder = APIHelper.append_url_with_template_parameters(query_builder, { 
            "id": id
        })

        # Validate and preprocess url
        query_url = APIHelper.clean_url(query_builder)

        # Prepare headers
        headers = {

            "user-agent": "batchly/0.7.1",

        }

        #append custom auth authorization
        CustomAuthUtility.appendCustomAuthParams(query_url, 'DELETE', headers)

        # Prepare and invoke the API call request to fetch the response
        response = unirest.delete(query_url, headers=headers)

        # Error handling using HTTP status codes
        if response.code == 404:
            raise APIException("NotFound", 404, response.body)

        elif response.code < 200 or response.code > 206:  # 200 = HTTP OK
            raise APIException("HTTP Response Not OK", response.code, response.body)
        
