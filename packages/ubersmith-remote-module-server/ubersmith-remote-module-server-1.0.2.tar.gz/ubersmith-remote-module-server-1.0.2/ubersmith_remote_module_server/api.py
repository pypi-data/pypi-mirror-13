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


class Api(object):
    def __init__(self, app, router):
        self.app = app
        self.router = router

        app.add_url_rule('/<module_name>/', view_func=self.list_implemented_methods, methods=['GET'])
        app.add_url_rule('/<module_name>/', view_func=self.handle_remote_invocation, methods=['POST'])


    def list_implemented_methods(self, module_name):
        return json_response({
            'implemented_methods': self.router.list_implemented_methods(module_name)
        }, 200)

    def handle_remote_invocation(self, module_name):
        data = request.get_json()
        output = self.router.invoke_method(module_name=module_name, **data)
        return json_response(output, 200)

def json_response(data, code):
    json_data = json.dumps(data, indent=None)
    response = current_app.response_class(json_data, mimetype='application/json; charset=UTF-8')
    response.status_code = code

    return response