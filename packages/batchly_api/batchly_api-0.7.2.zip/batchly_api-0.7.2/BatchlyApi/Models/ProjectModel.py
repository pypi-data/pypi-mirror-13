# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.ProjectModel
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Models.Platform import Platform

class ProjectModel(object):

    """Implementation of the 'ProjectModel' model.

    TODO: type model description here.

    Attributes:
        account_id (string): TODO: type description here.
        account_name (string): TODO: type description here.
        active_job_count (int): TODO: type description here.
        platform (Platform): TODO: type description here.
        id (string): TODO: type description here.
        name (string): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the ProjectModel class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    AccountId -- string -- Sets the attribute account_id
                    AccountName -- string -- Sets the attribute account_name
                    ActiveJobCount -- int -- Sets the attribute active_job_count
                    Platform -- Platform -- Sets the attribute platform
                    Id -- string -- Sets the attribute id
                    Name -- string -- Sets the attribute name
        
        """
        # Set all of the parameters to their default values
        self.account_id = None
        self.account_name = None
        self.active_job_count = None
        self.platform = None
        self.id = None
        self.name = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "AccountId": "account_id",
            "AccountName": "account_name",
            "ActiveJobCount": "active_job_count",
            "Platform": "platform",
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
            "account_id": "AccountId",
            "account_name": "AccountName",
            "active_job_count": "ActiveJobCount",
            "platform": "Platform",
            "id": "Id",
            "name": "Name",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)