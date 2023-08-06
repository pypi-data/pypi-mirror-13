# Copyright (c) 2016 Justin Hammond
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click
import requests

import pyresty.utils as utils
            

def handle_request(method, path, conf_info, additional_args, headers,
                   query_strings, data=None):
    result = utils.parse_conf_stuff(conf_info)
    final_path = path if path is not None else ""
    root_path = result.get('path', '')
    host = result.get('host')
    query_dict = utils.qs_to_dict(query_strings, result.get('query', {}))
    header_dict = utils.head_to_dict(headers, result.get('headers', {}))
    if len(root_path) > 0:
        join_character = "/"
        if root_path.endswith("/") or final_path.startswith("/"):
            join_character = ""
        final_path = "%s%s%s" % (root_path, join_character, final_path)
    full_path = "%s%s" % (host, final_path)
    if method == "GET":
        resp = requests.get(full_path, params=query_dict, headers=header_dict)
    if method == "DELETE":
        resp = requests.delete(full_path, params=query_dict,
                               headers=header_dict)
    if method == "POST":
        resp = requests.post(full_path, params=query_dict, data=data,
                             headers=header_dict)
    if method == "PUT":
        resp = requests.put(full_path, params=query_dict, data=data,
                            headers=header_dict)
    if method == "PATCH":
        resp = requests.patch(full_path, params=query_dict, data=data,
                              headers=header_dict)
    if resp.status_code not in (204, 205):
        click.echo(resp.text)
    return resp.status_code
