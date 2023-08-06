# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.JobModel
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper

class JobModel(object):

    """Implementation of the 'JobModel' model.

    TODO: type model description here.

    Attributes:
        runs (double): TODO: type description here.
        is_scheduled (bool): TODO: type description here.
        is_executing (bool): TODO: type description here.
        id (string): TODO: type description here.
        name (string): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the JobModel class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    Runs -- double -- Sets the attribute runs
                    IsScheduled -- bool -- Sets the attribute is_scheduled
                    IsExecuting -- bool -- Sets the attribute is_executing
                    Id -- string -- Sets the attribute id
                    Name -- string -- Sets the attribute name
        
        """
        # Set all of the parameters to their default values
        self.runs = None
        self.is_scheduled = None
        self.is_executing = None
        self.id = None
        self.name = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "Runs": "runs",
            "IsScheduled": "is_scheduled",
            "IsExecuting": "is_executing",
            "Id": "id",
            "Name": "name",
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
            "runs": "Runs",
            "is_scheduled": "IsScheduled",
            "is_executing": "IsExecuting",
            "id": "Id",
            "name": "Name",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)