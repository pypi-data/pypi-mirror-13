import unittest
from os import getenv

import pyrax
from datastore.core.test.test_basic import TestDatastore

from cloudfiles import RackspaceCloudFilesDatastore


RACKSPACE_USERNAME = getenv('RACKSPACE_USERNAME')
RACKSPACE_API_KEY = getenv('RACKSPACE_API_KEY')
RACKSPACE_REGION = getenv('RACKSPACE_REGION')


class TestRackspaceCloudFilesDatastore(TestDatastore):

    container_name = 'datastore-test'

    def setUp(self):
        pyrax.set_setting('identity_type', 'rackspace')
        pyrax.set_default_region(RACKSPACE_REGION)
        pyrax.set_credentials(RACKSPACE_USERNAME, RACKSPACE_API_KEY)
        self.container = pyrax.cloudfiles.create_container(self.container_name)
        self.container.delete_all_objects()

    def tearDown(self):
        self.container.delete(del_objects=True)

    def test(self):
        store = RackspaceCloudFilesDatastore(self.container)
        self.subtest_simple([store], numelems=20)


if __name__ == '__main__':
    unittest.main()
