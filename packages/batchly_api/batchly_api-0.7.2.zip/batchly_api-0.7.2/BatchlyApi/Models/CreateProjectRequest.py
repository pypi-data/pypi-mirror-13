# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.CreateProjectRequest
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Models.VpcDetails import VpcDetails

class CreateProjectRequest(object):

    """Implementation of the 'CreateProjectRequest' model.

    TODO: type model description here.

    Attributes:
        account_id (string): TODO: type description here.
        name (string): TODO: type description here.
        vpc (VpcDetails): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the CreateProjectRequest class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    AccountId -- string -- Sets the attribute account_id
                    Name -- string -- Sets the attribute name
                    Vpc -- VpcDetails -- Sets the attribute vpc
        
        """
        # Set all of the parameters to their default values
        self.account_id = None
        self.name = None
        self.vpc = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "AccountId": "account_id",
            "Name": "name",
            "Vpc": "vpc",
        }

        # Parse all of the Key-Value arguments
        if kwargs is not None:
            for key in kwargs:
                # Only add arguments that are actually part of this object
                if key in replace_names:
                    setattr(self, replace_names[key], kwargs[key])

            # Other objects also need to be initialised properly
            if "Vpc" in kwargs:
                self.vpc = VpcDetails(**kwargs["Vpc"])

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
            "name": "Name",
            "vpc": "Vpc",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)