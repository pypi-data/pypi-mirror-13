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

import mock
import unittest

from ubersmith_remote_module_server import server


class TestModule(object):
    def hello(self):
        return "world"

@mock.patch('ubersmith_remote_module_server.server.Flask')
@mock.patch('ubersmith_remote_module_server.server.router.Router')
@mock.patch('ubersmith_remote_module_server.server.api.Api')
class ServerTest(unittest.TestCase):
    def test_starting_a_server(self, api_mock, router_mock, flask_mock):
        router_instance = router_mock.return_value
        flask_instance = flask_mock.return_value

        modules = {'test_module': TestModule()}
        s = server.Server(modules)
        s.run()

        router_mock.assert_called_with()
        api_mock.assert_called_with(modules, flask_instance, router_instance)
        flask_instance.run.assert_called_with()

    def test_run_passes_parameters_to_flask(self, api_mock, router_mock, flask_mock):
        flask_instance = flask_mock.return_value

        s = server.Server({})
        s.run('param1', 'param2', kwarg1='test')
        flask_instance.run.assert_called_with('param1', 'param2', kwarg1='test')
