"""
The **drf-ember** helpers support business logic in other classes and functions by
maintaining some internal state and providing methods to operate on that state.
"""
import inflection


class IncludedHelper(object):
    """
    A helper class for managing a JSON API document's ``included`` member.

    Note:
        Expects primary keys to be **strings**, per the JSON API.
    """
    def __init__(self):
        """
        Creates a ``_resources`` class instance property for holding a list
        of resources for assignment to a JSON API document's ``included``. Also
        creates a ``_key_inventory`` to facilitate checking which primary keys
        for each resource ``type`` have been added to ``_resources``. The JSON API
        specification requires a single, canonical representation each ``type``\``id`` pair
        in a response document.
        """
        self._resources = list()
        self._key_inventory = {}

    def is_included(self, resource):
        """
        Checks if a resource is already in the helper's ``included``.

        Arguments:
            resource (dict): Typically, a dict representation of a persisted Django model.

        Returns:
            True if the primary key for the resource ``type`` is already a part
            of the helper's included resources. False otherwise.
        """
        resource_type = resource['type']
        resource_type = inflection.dasherize(resource_type)
        if resource_type in self._key_inventory:
            current_primary_keys = self._key_inventory[resource_type]
            return True if resource['id'] in current_primary_keys else False
        else:
            return False

    def add_resource(self, resource):
        """
        Adds a resource not previously added into the helper.

        Arguments:
            resource (dict): Typically, a dict representation of a persisted Django model.

        Returns:
            True if the resource was appended to the helper's included resources.
            False otherwise.
        """
        if not self.is_included(resource):
            self._resources.append(resource)
            resource_type = resource['type']
            resource_type = inflection.dasherize(resource_type)
            if resource_type in self._key_inventory:
                self._key_inventory[resource_type].append(resource['id'])
            else:
                self._key_inventory[resource_type] = [resource['id']]
            return True
        else:
            # Not added because the 'type' and 'id' combo already exists
            return False

    @property
    def empty(self):
        """
        Checks helper emptiness.

        Returns:
            True if there is one or more resources 'saved' in the helper. False otherwise.
        """
        return False if self._resources else True

    def get_included(self):
        """
        Provides the current state of resources saved in the helper.

        Returns:
            A list of resource dictionaries.
        """
        return self._resources