# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import testtools

import shade
from shade import meta
from shade import _utils
from shade.tests.unit import base
from shade.tests import fakes


RAW_ROLE_ASSIGNMENTS = [
    {
        "links": {"assignment": "http://example"},
        "role": {"id": "123456"},
        "scope": {"domain": {"id": "161718"}},
        "user": {"id": "313233"}
    },
    {
        "links": {"assignment": "http://example"},
        "group": {"id": "101112"},
        "role": {"id": "123456"},
        "scope": {"project": {"id": "456789"}}
    }
]


class TestIdentityRoles(base.TestCase):

    def setUp(self):
        super(TestIdentityRoles, self).setUp()
        self.cloud = shade.operator_cloud(validate=False)

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_roles(self, mock_keystone):
        self.cloud.list_roles()
        self.assertTrue(mock_keystone.roles.list.called)

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_get_role(self, mock_keystone):
        role_obj = fakes.FakeRole(id='1234', name='fake_role')
        mock_keystone.roles.list.return_value = [role_obj]

        role = self.cloud.get_role('fake_role')

        self.assertTrue(mock_keystone.roles.list.called)
        self.assertIsNotNone(role)
        self.assertEqual('1234', role['id'])
        self.assertEqual('fake_role', role['name'])

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_create_role(self, mock_keystone):
        role_name = 'tootsie_roll'
        role_obj = fakes.FakeRole(id='1234', name=role_name)
        mock_keystone.roles.create.return_value = role_obj

        role = self.cloud.create_role(role_name)

        mock_keystone.roles.create.assert_called_once_with(
            name=role_name
        )
        self.assertIsNotNone(role)
        self.assertEqual(role_name, role['name'])

    @mock.patch.object(shade.OperatorCloud, 'get_role')
    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_delete_role(self, mock_keystone, mock_get):
        role_obj = fakes.FakeRole(id='1234', name='aaa')
        mock_get.return_value = meta.obj_to_dict(role_obj)
        self.assertTrue(self.cloud.delete_role('1234'))
        self.assertTrue(mock_keystone.roles.delete.called)

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments(self, mock_keystone):
        mock_keystone.role_assignments.list.return_value = RAW_ROLE_ASSIGNMENTS
        ret = self.cloud.list_role_assignments()
        mock_keystone.role_assignments.list.assert_called_once_with()
        normalized_assignments = _utils.normalize_role_assignments(
            RAW_ROLE_ASSIGNMENTS
        )
        self.assertEqual(normalized_assignments, ret)

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments_filters(self, mock_keystone):
        params = dict(user='123', domain='456', effective=True)
        self.cloud.list_role_assignments(filters=params)
        mock_keystone.role_assignments.list.assert_called_once_with(**params)

    @mock.patch.object(shade.OpenStackCloud, 'keystone_client')
    def test_list_role_assignments_exception(self, mock_keystone):
        mock_keystone.role_assignments.list.side_effect = Exception()
        with testtools.ExpectedException(
            shade.OpenStackCloudException,
            "Failed to list role assignments"
        ):
            self.cloud.list_role_assignments()
