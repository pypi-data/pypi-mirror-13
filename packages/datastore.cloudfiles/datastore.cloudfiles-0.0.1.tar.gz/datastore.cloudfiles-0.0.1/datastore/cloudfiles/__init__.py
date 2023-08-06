import json

from datastore.core import Datastore
from pyrax.exceptions import NoSuchObject


class RackspaceCloudFilesDatastore(Datastore):
    """Rackspace Cloud Files datastore implemented over the Pyrax library.
    """

    def __init__(self, container):
        """Initialise datastore with Pyrax cloud files container.

        :param container: Cloud Files container to use.
        """
        self.container = container

    def serialised_value(self, value):
        return json.dumps(value) if value is not None else None

    def deserialised_value(self, storage_obj):
        return json.loads(storage_obj.get()) if storage_obj is not None else None

    def put(self, key, value):
        """Store the object `value` named by `key`.

        :param key: Key naming `value`
        :param value: object to store
        """
        self.container.create(obj_name=str(key), data=self.serialised_value(value), content_type='application/json')

    def get(self, key):
        """Return the object named by key or None if it does not exist.

        :param key: Key naming the object to retrieve
        :return: object or None
        """
        try:
            return self.deserialised_value(self.container.get_object(str(key)))
        except NoSuchObject:
            return None

    def contains(self, key):
        return str(key) in self.container.get_object_names()

    def delete(self, key):
        """Removes the object named by `key`.

        :param key: Key naming the object to remove.
        """
        try:
            self.container.delete_object(str(key))
        except NoSuchObject:
            pass

    def query(self, query):
        """Returns an iterable of objects matching criteria expressed in `query`.

        Implementations of query will be the largest differentiating factor
        amongst datastores. All datastores **must** implement query, even using
        query's worst case scenario, see :ref:class:`Query` for details.

        :param query: Query object describing the objects to return.
        :return: iterable cursor with all objects matching criteria
        """
        return query((self.deserialised_value(x) for x in self.container.get_objects(prefix=query.key)))
