# Copyright 2016 Internap
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask
from hamcrest import assert_that, is_
import json
import mock
import unittest

from ubersmith_remote_module_server.api import Api


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask('test_app')
        self.api_client = self.app.test_client()
        self.router = mock.Mock()
        self.module1 = mock.Mock()
        self.module2 = mock.Mock()
        self.modules = {'module1': self.module1,
                        'module2': self.module2}

        self.api = Api(self.modules, self.app, self.router)

    def generate_module_path(self, module_name):
        return '/{0}/'.format(module_name)

    def test_list_implemented_methods(self):
        self.router.list_implemented_methods.return_value = ['abcd', 'efgh']

        output = self.api_client.get(self.generate_module_path('module1'))
        self.router.list_implemented_methods.assert_called_with(self.module1)

        assert_that(json.loads(output.data.decode(output.charset)), is_({
            "implemented_methods": [
                "abcd",
                "efgh"
            ]
        }))

    def test_execute_method_returns_string(self):
        self.router.invoke_method.return_value = 'simple string'
        output = self.api_client.post(self.generate_module_path('module2'),
                                      headers={'Content-Type': 'application/json'},
                                      data=json.dumps(
            {
                "method": "remote_method",
                "params": [],
                "env": {
                    "variable1": "value1"
                },
                "callback": {}
            }
        ))

        self.router.invoke_method.assert_called_with(module=self.module2, method='remote_method', params=[], env={'variable1': 'value1'}, callback={})
        assert_that(json.loads(output.data.decode(output.charset)), is_('simple string'))

    def test_execute_method_returns_list(self):
        self.router.invoke_method.return_value = ['a', 'b', 'c']
        output = self.api_client.post(self.generate_module_path('module2'),
                                      headers={'Content-Type': 'application/json'},
                                      data=json.dumps(
            {
                "method": "remote_method",
                "params": [],
                "env": {
                    "variable1": "value1"
                },
                "callback": {}
            }
        ))

        self.router.invoke_method.assert_called_with(module=self.module2, method='remote_method', params=[], env={'variable1': 'value1'}, callback={})
        assert_that(json.loads(output.data.decode(output.charset)), is_(['a', 'b', 'c']))

    def test_invoking_unknown_module_returns_a_404(self):
        output = self.api_client.post(self.generate_module_path('new_module'),
                                      headers={'Content-Type': 'application/json'},
                                      data=json.dumps(
                                          {
                                              "method": "remote_method",
                                              "params": [],
                                              "env": {
                                                  "variable1": "value1"
                                              },
                                              "callback": {}
                                          }
                                      ))

        assert_that(output.status_code, is_(404))

    def test_listing_unknown_module_returns_a_404(self):
        output = self.api_client.get(self.generate_module_path('new_module'))

        assert_that(output.status_code, is_(404))

class NoTrailingSlashApiTest(ApiTest):
    def generate_module_path(self, module_name):
        return '/{0}'.format(module_name)