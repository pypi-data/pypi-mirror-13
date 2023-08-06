# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.AddAWSAccountRequest
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper

class AddAWSAccountRequest(object):

    """Implementation of the 'AddAWSAccountRequest' model.

    TODO: type model description here.

    Attributes:
        name (string): TODO: type description here.
        access_key (string): TODO: type description here.
        secret_key (string): TODO: type description here.
        base_region (string): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the AddAWSAccountRequest class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    Name -- string -- Sets the attribute name
                    AccessKey -- string -- Sets the attribute access_key
                    SecretKey -- string -- Sets the attribute secret_key
                    BaseRegion -- string -- Sets the attribute base_region
        
        """
        # Set all of the parameters to their default values
        self.name = None
        self.access_key = None
        self.secret_key = None
        self.base_region = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "Name": "name",
            "AccessKey": "access_key",
            "SecretKey": "secret_key",
            "BaseRegion": "base_region",
        }

        # Parse all of the Key-Value arguments
        if kwargs is not None:
            for key in kwargs:
                # Only add arguments that are actually part of this object
                if key in replace_names:
                    setattr(self, replace_names[key], kwargs[key])

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
            "name": "Name",
            "access_key": "AccessKey",
            "secret_key": "SecretKey",
            "base_region": "BaseRegion",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)