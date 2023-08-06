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

import os
import shlex
import urlparse

import click
import configobj

import pyresty.globals as glob


def load_conf(config):
    conf_file = config
    if conf_file is None:
        home_dir = os.path.expanduser('~')
        conf_file = "%s/%s" % (home_dir, ".pyresty")
    conf = configobj.ConfigObj(conf_file, raise_errors=True)
    if glob.HOSTS not in conf and glob.CONF not in conf:
        click.echo("Configuration file invalid")
        exit(1)
    return conf


def _fast_uniquify(seq, idfun=None):
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


def validate_host(host, require_scheme=False):
    parse = urlparse.urlparse(host)
    if len(parse.netloc) == 0:
        return False
    if require_scheme and len(parse.scheme) == 0:
        return False
    return True


def parse_conf_stuff(conf_info):
    (host, args) = conf_info.split(" ", 1)
    parse = urlparse.urlparse(host)
    scheme = parse.scheme if len(parse.scheme) > 0 else "http"
    host = "%s://%s" % (scheme, parse.netloc)
    query_string_dict = {}
    if len(parse.query) > 0:
        query_string_dict = urlparse.parse_qs(parse.query)

    tokens = shlex.split(args)
    headers = {}
    while tokens is not None and len(tokens) > 0:
        curr_token = tokens.pop(0)
        if curr_token == '-H':
            if len(tokens) == 0: continue
            (header, value) = tokens.pop(0).split(':', 1)
            headers[header] = value

    result = dict(host=host, path=parse.path, params=parse.params,
                  headers=headers, query=query_string_dict,
                  fragment=parse.fragment)
    return result


def qs_to_dict(query_params, query_conf):
    query_dict = dict()
    for qp in query_params:
        if "=" not in qp: continue
        (attr, value) = qp.split("=", 1)
        if attr not in query_dict: query_dict[attr] = list()
        query_dict[attr].append(value)
    for key, val in query_conf.iteritems():
        """<val> is expected to be a list due to urlparse."""
        if key in query_dict:
            query_dict[key] = utils._fast_uniquify(query_dict[key] + val)
        else: query_dict[key] = val
    return query_dict


def head_to_dict(header_params, header_conf_dict):
    header_dict = dict()
    for header in header_params:
        if ":" not in header: continue
        (attr, value) = header.split(":", 2)
        header_dict[attr] = value
    for key, value in header_conf_dict.items():
        header_dict[unicode(key)] = unicode(value)
    return header_dict
