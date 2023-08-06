# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.AccountModel
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Models.Platform import Platform

class AccountModel(object):

    """Implementation of the 'AccountModel' model.

    TODO: type model description here.

    Attributes:
        active_processor_count (double): TODO: type description here.
        active_project_count (double): TODO: type description here.
        platform (Platform): TODO: type description here.
        platform_name (string): TODO: type description here.
        id (string): TODO: type description here.
        name (string): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the AccountModel class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    ActiveProcessorCount -- double -- Sets the attribute active_processor_count
                    ActiveProjectCount -- double -- Sets the attribute active_project_count
                    Platform -- Platform -- Sets the attribute platform
                    PlatformName -- string -- Sets the attribute platform_name
                    Id -- string -- Sets the attribute id
                    Name -- string -- Sets the attribute name
        
        """
        # Set all of the parameters to their default values
        self.active_processor_count = None
        self.active_project_count = None
        self.platform = None
        self.platform_name = None
        self.id = None
        self.name = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "ActiveProcessorCount": "active_processor_count",
            "ActiveProjectCount": "active_project_count",
            "Platform": "platform",
            "PlatformName": "platform_name",
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
            if "Platform" in kwargs:
                self.platform = Platform.from_string(kwargs["Platform"])

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
            "active_processor_count": "ActiveProcessorCount",
            "active_project_count": "ActiveProjectCount",
            "platform": "Platform",
            "platform_name": "PlatformName",
            "id": "Id",
            "name": "Name",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)