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

from hamcrest import is_, assert_that
import mock
import unittest

from ubersmith_remote_module_server.router import Router


class Module3(object):
    def ab(self):
        pass

    def cd(self):
        pass

    def _ef(self):
        pass

    def __gh(self):
        pass


class RouterTest(unittest.TestCase):
    def setUp(self):
        self.module1 = mock.Mock()
        self.module1.my_method_name.return_value = 'yes'
        self.module2 = mock.Mock()
        self.module2.hello.return_value = 'world'
        self.module3 = Module3()

        self.modules = {'module1': self.module1,
                        'module2': self.module2,
                        'module3': self.module3}

        self.basic_router = Router(env_as_kwarg=False)
        self.router = Router()

    def test_basic_mode(self):
        result = self.basic_router.invoke_method(module=self.module1, method='my_method_name',
                                                 params=['value1', 'value2'])

        self.module1.my_method_name.assert_called_with('value1', 'value2')
        assert_that(result, is_('yes'))

    def test_env_is_optionally_passed_as_keyword_argument_in_every_call(self):
        result = self.router.invoke_method(module=self.module2, method='hello',
                                           params=['value1', 'value2'],
                                           env={'local_variable1': 'value1', 'local_variable2': 'value2'})

        self.module2.hello.assert_called_with('value1', 'value2',
                                              env={'local_variable1': 'value1', 'local_variable2': 'value2'})
        assert_that(result, is_('world'))

    def test_list_implemented_methods(self):
        result = self.router.list_implemented_methods(self.module3)

        assert_that(result, is_(['ab', 'cd']))

    def test_accept_callback_as_kwarg(self):
        self.router.invoke_method(module=self.module1, method='hello', params=[], env={},
                                  callback={'url': 'http://example.net', 'params': {'k1': 'v1', 'k2': 'v2'}})
