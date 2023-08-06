# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.AddParameterGroupRequest
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Models.KeyValuePairStringString import KeyValuePairStringString

class AddParameterGroupRequest(object):

    """Implementation of the 'AddParameterGroupRequest' model.

    TODO: type model description here.

    Attributes:
        name (string): TODO: type description here.
        parameter_values (list of KeyValuePairStringString): TODO: type
            description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the AddParameterGroupRequest class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    Name -- string -- Sets the attribute name
                    ParameterValues -- list of KeyValuePairStringString -- Sets the attribute parameter_values
        
        """
        # Set all of the parameters to their default values
        self.name = None
        self.parameter_values = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "Name": "name",
            "ParameterValues": "parameter_values",
        }

        # Parse all of the Key-Value arguments
        if kwargs is not None:
            for key in kwargs:
                # Only add arguments that are actually part of this object
                if key in replace_names:
                    setattr(self, replace_names[key], kwargs[key])

            # Other objects also need to be initialised properly
            if "ParameterValues" in kwargs:
                # Parameter is an array, so we need to iterate through it
                self.parameter_values = list()
                for item in kwargs["ParameterValues"]:
                    self.parameter_values.append(KeyValuePairStringString(**item))

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
            "parameter_values": "ParameterValues",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)