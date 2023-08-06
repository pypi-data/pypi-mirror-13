# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.CustomImage
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper

class CustomImage(object):

    """Implementation of the 'CustomImage' model.

    TODO: type model description here.

    Attributes:
        enabled (bool): TODO: type description here.
        image_id (string): TODO: type description here.
        region (string): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the CustomImage class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    Enabled -- bool -- Sets the attribute enabled
                    ImageId -- string -- Sets the attribute image_id
                    Region -- string -- Sets the attribute region
        
        """
        # Set all of the parameters to their default values
        self.enabled = None
        self.image_id = None
        self.region = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "Enabled": "enabled",
            "ImageId": "image_id",
            "Region": "region",
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
            "enabled": "Enabled",
            "image_id": "ImageId",
            "region": "Region",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)