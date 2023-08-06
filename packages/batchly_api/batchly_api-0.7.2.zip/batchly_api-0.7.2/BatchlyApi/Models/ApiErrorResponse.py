# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.ApiErrorResponse
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper

class ApiErrorResponse(object):

    """Implementation of the 'ApiErrorResponse' model.

    TODO: type model description here.

    Attributes:
        message (string): TODO: type description here.
        model_state (mixed): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the ApiErrorResponse class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    Message -- string -- Sets the attribute message
                    ModelState -- mixed -- Sets the attribute model_state
        
        """
        # Set all of the parameters to their default values
        self.message = None
        self.model_state = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "Message": "message",
            "ModelState": "model_state",
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
            "message": "Message",
            "model_state": "ModelState",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)