# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.ProcessorModel
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Models.RequestType import RequestType
from BatchlyApi.Models.ResponseType import ResponseType

class ProcessorModel(object):

    """Implementation of the 'ProcessorModel' model.

    TODO: type model description here.

    Attributes:
        account_name (string): TODO: type description here.
        account_id (string): TODO: type description here.
        request_type (RequestType): TODO: type description here.
        response_type (ResponseType): TODO: type description here.
        active_job_count (int): TODO: type description here.
        id (string): TODO: type description here.
        name (string): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the ProcessorModel class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    AccountName -- string -- Sets the attribute account_name
                    AccountId -- string -- Sets the attribute account_id
                    RequestType -- RequestType -- Sets the attribute request_type
                    ResponseType -- ResponseType -- Sets the attribute response_type
                    ActiveJobCount -- int -- Sets the attribute active_job_count
                    Id -- string -- Sets the attribute id
                    Name -- string -- Sets the attribute name
        
        """
        # Set all of the parameters to their default values
        self.account_name = None
        self.account_id = None
        self.request_type = None
        self.response_type = None
        self.active_job_count = None
        self.id = None
        self.name = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "AccountName": "account_name",
            "AccountId": "account_id",
            "RequestType": "request_type",
            "ResponseType": "response_type",
            "ActiveJobCount": "active_job_count",
            "Id": "id",
            "Name": "name",
        }

        # Parse all of the Key-Value arguments
        if kwargs is not None:
            for key in kwargs:
                # Only add arguments that are actually part of this object
                if key in replace_names:
                    setattr(self, replace_names[key], kwargs[key])

            # Other objects also need to be initialised properly
            if "RequestType" in kwargs:
                self.request_type = RequestType.from_string(kwargs["RequestType"])

            # Other objects also need to be initialised properly
            if "ResponseType" in kwargs:
                self.response_type = ResponseType.from_string(kwargs["ResponseType"])

    def resolve_names(self):
        """Creates a dictionary representation of this object.
        
        This method converts an object to a dictionary that represents the
        format that the model should be in when passed into an API Request.
        Because of this, the generated dictionary may have different
        property names to that of the model itself.
        
        Returns:
            dict: The dictionary representing the object.
        
        """
        # Create a mapping from Model property names to API property names
        replace_names = {
            "account_name": "AccountName",
            "account_id": "AccountId",
            "request_type": "RequestType",
            "response_type": "ResponseType",
            "active_job_count": "ActiveJobCount",
            "id": "Id",
            "name": "Name",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)