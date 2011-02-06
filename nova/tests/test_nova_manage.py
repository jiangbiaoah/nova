# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Tests For Nova-Manage
"""

import os
import subprocess

from nova import test


class NovaManageTestCase(test.TestCase):
    """Test case for nova-manage"""
    def setUp(self):
        super(NovaManageTestCase, self).setUp()

    def teardown(self):
        fnull.close()

    def test_create_and_delete_instance_types(self):
        fnull = open(os.devnull, 'w')
        retcode = subprocess.call(["bin/nova-manage", "instance_type",\
                                    "create", "test", "256", "1",\
                                    "120", "99"], stdout=fnull)
        self.assertEqual(0, retcode)
        retcode = subprocess.call(["bin/nova-manage", "instance_type",\
                                    "delete", "test"], stdout=fnull)
        self.assertEqual(0, retcode)

    def test_list_instance_types_or_flavors(self):
        fnull = open(os.devnull, 'w')
        for c in ["instance_type", "flavor"]:
            retcode = subprocess.call(["bin/nova-manage", c, \
                                        "list"], stdout=fnull)
            self.assertEqual(0, retcode)

    def test_list_specific_instance_type(self):
        fnull = open(os.devnull, 'w')
        retcode = subprocess.call(["bin/nova-manage", "instance_type", "list",
                                    "m1.medium"], stdout=fnull)
        self.assertEqual(0, retcode)

    def test_should_raise_on_bad_create_args(self):
        fnull = open(os.devnull, 'w')
        retcode = subprocess.call(["bin/nova-manage", "instance_type",\
                                    "create", "test", "256", "0",\
                                    "120", "99"], stdout=fnull)
        self.assertEqual(1, retcode)

    def test_should_fail_on_duplicate_flavorid(self):
        fnull = open(os.devnull, 'w')
        retcode = subprocess.call(["bin/nova-manage", "instance_type",\
                                    "create", "test", "256", "1",\
                                    "120", "1"], stdout=fnull)
        self.assertEqual(1, retcode)

    def test_instance_type_delete_should_fail_without_valid_name(self):
        fnull = open(os.devnull, 'w')
        retcode = subprocess.call(["bin/nova-manage", "instance_type",\
                                    "delete", "saefasff"], stdout=fnull)
        self.assertEqual(1, retcode)
