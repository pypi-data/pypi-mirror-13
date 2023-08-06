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

import json
from flask import request, current_app
import functools


class Api(object):
    def __init__(self, modules, app, router):
        self.app = app
        self.router = router
        self.app.url_map.strict_slashes = False

        for module_name, module in modules.items():
            list_endpoint = functools.partial(self.list_implemented_methods, module)
            list_endpoint.__name__ = "list_" + module_name
            app.add_url_rule('/{}'.format(module_name), view_func=list_endpoint, methods=['GET'])

            handle_endpoint = functools.partial(self.handle_remote_invocation, module)
            handle_endpoint.__name__ = "handle_" + module_name
            app.add_url_rule('/{}'.format(module_name), view_func=handle_endpoint, methods=['POST'])

    def list_implemented_methods(self, module):
        methods = self.router.list_implemented_methods(module)
        return json_response({'implemented_methods': methods}, 200)

    def handle_remote_invocation(self, module):
        data = request.get_json()
        output = self.router.invoke_method(module=module, **data)
        return json_response(output, 200)

def json_response(data, code):
    json_data = json.dumps(data, indent=None)
    response = current_app.response_class(json_data, mimetype='application/json; charset=UTF-8')
    response.status_code = code

    return response
