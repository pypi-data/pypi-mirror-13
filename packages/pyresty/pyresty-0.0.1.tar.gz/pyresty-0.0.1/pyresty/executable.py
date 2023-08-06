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

import pyresty.globals as glob
import pyresty.request as req
import pyresty.utils as utils



command_settings = {
    'ignore_unknown_options': True,
}


def current_host(conf):
    return conf[glob.CONF].get('current')


def _do_wrap(context, method, path, options, config, h, q, data=None):
    conf = utils.load_conf(config)
    current = current_host(conf)
    if current is None:
        click.echo("No current host set")
        exit(1)
    code = req.handle_request(method, path, conf[glob.HOSTS][current], options, h,
                              q, data=data)
    if code >= 400:
        exit(1)
    exit(0)


def commonclick(func):
    @click.command(context_settings=command_settings)
    @click.argument('path', default=None, required=False)
    @click.argument('options', nargs=-1)
    @click.option('--config', default=None, is_flag=False,
                  type=click.File('rb'),
                  help='Configuration file; defaults to ~/.pyresty')
    @click.option('-H', default=None, multiple=True, nargs=1,
                  is_flag=False, metavar="HTTP_HEADER",
                  help="Headers; can be used multiple times")
    @click.option('-q', default=None, multiple=True, nargs=1,
                  is_flag=False, metavar="attribute=value",
                  help="Query string; can be used multiple times")
    @click.pass_context
    def inner(*a, **kw):
        func(*a, **kw)
    return inner


@commonclick
def do_get(context, path, options, config, h, q):
    _do_wrap(context, "GET", path, options, config, h, q)


@commonclick
def do_delete(context, path, options, config, h, q):
    _do_wrap(context, "DELETE", path, options, config, h, q)


@click.option('-d', default=None, nargs=1,
              is_flag=False, metavar="'<some data>'",
              help="Data for PUT")
@commonclick
def do_put(context, path, options, config, h, q, d):
    _do_wrap(context, "PUT", path, options, config, h, q, data=d)


@click.option('-d', default=None, nargs=1,
              is_flag=False, metavar="'<some data>'",
              help="Data for PATCH")
@commonclick
def do_patch(context, path, options, config, h, q, d):
    _do_wrap(context, "PATCH", path, options, config, h, q, data=d)


@click.option('-d', default=None, nargs=1,
              is_flag=False, metavar="'<some data>'",
              help="Data for POST")
@commonclick
def do_post(context, path, options, config, h, q, d):
    _do_wrap(context, "POST", path, options, config, h, q, data=d)


@click.command(context_settings=command_settings)
@click.argument('command', default=None, required=False)
@click.argument('arguments', nargs=-1)
@click.option('--config', default=None, is_flag=False,
              type=click.File('rb'),
              help='Configuration file; defaults to ~/.pyresty')
@click.pass_context
def main_run(context, command, arguments, config):
    commands = ['add', 'remove', 'set', 'list', 'change']
    cmd_arg_list = list(arguments)
    conf = utils.load_conf(config, glob.HOSTS, glob.CONF)
    if command is None:
        current = current_host(conf)
        if current is None:
            click.echo("No current host set")
        else:
            click.echo("%s:%s" % (current, conf[glob.HOSTS][current]))
            exit(0)
    if command in commands:
        if command == 'list':
            for host in conf[glob.HOSTS]:
                click.echo("%s:%s" % (host, conf[glob.HOSTS][host]))
            exit(0)
        if command == 'change':
            host = cmd_arg_list.pop(0)
            info = " ".join(cmd_arg_list)
            if not utils.validate_host(info):
                click.echo("Invalid host setting.")
                exit(1)
            if host not in conf[glob.HOSTS]:
                click.echo("Host '%s' not defined" % host)
                exit(1)
            conf[glob.HOSTS][host] = info
            conf.write()
            exit(0)
        if command == 'add':
            host = cmd_arg_list.pop(0)
            info = " ".join(cmd_arg_list)
            if not utils.validate_host(info):
                click.echo("Invalid host setting.")
                exit(1)
            if host in conf[glob.HOSTS]:
                click.echo("Host '%s' already defined" % host)
                exit(1)
            conf[glob.HOSTS][host] = info
            conf.write()
            exit(0)
        if command == 'remove':
            host = cmd_arg_list.pop(0)
            if host not in conf[glob.HOSTS]:
                click.echo("Host '%s' not configured" % host)
                exit(1)
            del conf[glob.HOSTS][host]
            conf.write()
            exit(0)
    else:
        if command not in conf[glob.HOSTS]:
            click.echo("Host '%s' not configured" % command)
            exit(1)
        conf[glob.CONF]['current'] = command
        conf.write()
