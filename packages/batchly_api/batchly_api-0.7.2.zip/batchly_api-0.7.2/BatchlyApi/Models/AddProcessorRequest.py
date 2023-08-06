# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.AddProcessorRequest
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Models.OperatingSystem import OperatingSystem
from BatchlyApi.Models.Language import Language
from BatchlyApi.Models.RequestType import RequestType
from BatchlyApi.Models.ResponseType import ResponseType
from BatchlyApi.Models.Parameter import Parameter
from BatchlyApi.Models.CustomImage import CustomImage

class AddProcessorRequest(object):

    """Implementation of the 'AddProcessorRequest' model.

    TODO: type model description here.

    Attributes:
        account_id (string): TODO: type description here.
        operating_system (OperatingSystem): TODO: type description here.
        language (Language): TODO: type description here.
        file_name (string): TODO: type description here.
        class_name (string): TODO: type description here.
        request_type (RequestType): TODO: type description here.
        response_type (ResponseType): TODO: type description here.
        package_location (string): TODO: type description here.
        parameters (list of Parameter): TODO: type description here.
        custom_image (CustomImage): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the AddProcessorRequest class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    AccountId -- string -- Sets the attribute account_id
                    OperatingSystem -- OperatingSystem -- Sets the attribute operating_system
                    Language -- Language -- Sets the attribute language
                    FileName -- string -- Sets the attribute file_name
                    ClassName -- string -- Sets the attribute class_name
                    RequestType -- RequestType -- Sets the attribute request_type
                    ResponseType -- ResponseType -- Sets the attribute response_type
                    PackageLocation -- string -- Sets the attribute package_location
                    Parameters -- list of Parameter -- Sets the attribute parameters
                    CustomImage -- CustomImage -- Sets the attribute custom_image
        
        """
        # Set all of the parameters to their default values
        self.account_id = None
        self.operating_system = None
        self.language = None
        self.file_name = None
        self.class_name = None
        self.request_type = None
        self.response_type = None
        self.package_location = None
        self.parameters = None
        self.custom_image = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "AccountId": "account_id",
            "OperatingSystem": "operating_system",
            "Language": "language",
            "FileName": "file_name",
            "ClassName": "class_name",
            "RequestType": "request_type",
            "ResponseType": "response_type",
            "PackageLocation": "package_location",
            "Parameters": "parameters",
            "CustomImage": "custom_image",
        }

        # Parse all of the Key-Value arguments
        if kwargs is not None:
            for key in kwargs:
                # Only add arguments that are actually part of this object
                if key in replace_names:
                    setattr(self, replace_names[key], kwargs[key])

            # Other objects also need to be initialised properly
            if "OperatingSystem" in kwargs:
                self.operating_system = OperatingSystem.from_string(kwargs["OperatingSystem"])

            # Other objects also need to be initialised properly
            if "Language" in kwargs:
                self.language = Language.from_string(kwargs["Language"])

            # Other objects also need to be initialised properly
            if "RequestType" in kwargs:
                self.request_type = RequestType.from_string(kwargs["RequestType"])

            # Other objects also need to be initialised properly
            if "ResponseType" in kwargs:
                self.response_type = ResponseType.from_string(kwargs["ResponseType"])

            # Other objects also need to be initialised properly
            if "Parameters" in kwargs:
                # Parameter is an array, so we need to iterate through it
                self.parameters = list()
                for item in kwargs["Parameters"]:
                    self.parameters.append(Parameter(**item))

            # Other objects also need to be initialised properly
            if "CustomImage" in kwargs:
                self.custom_image = CustomImage(**kwargs["CustomImage"])

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
            "account_id": "AccountId",
            "operating_system": "OperatingSystem",
            "language": "Language",
            "file_name": "FileName",
            "class_name": "ClassName",
            "request_type": "RequestType",
            "response_type": "ResponseType",
            "package_location": "PackageLocation",
            "parameters": "Parameters",
            "custom_image": "CustomImage",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)