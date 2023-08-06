#########################################################################
#  The MIT License (MIT)
#
#  Copyright (c) 2014~2015 CIVA LIN (林雪凡)
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##########################################################################


import configparser
import pathlib
import sys
import os
import signal

from . import defaultconfig


class ConfigError(Exception):
    pass


def get_config(rootdir):
    def read_config(rootdir):
        config = configparser.ConfigParser()
        config.read_dict(defaultconfig.DEFAULT_CONFIG)
        user_lolikitrc = pathlib.Path(
            os.path.expanduser('~')) / '.lolikitrc'
        if user_lolikitrc.is_file():
            config.read(str(user_lolikitrc))
        if rootdir is not None:
            project_lolikitrc = rootdir / '.loli' / 'lolikitrc'
            if project_lolikitrc.is_file():
                config.read(str(project_lolikitrc))
        return config

    def expand_config(config):
        config['default']['ignore_patterns'] += (
            '\n^\.loli($|' + os.sep + ')')
        return config

    def check_config(config):
        valid_newline_mode = ('posix', 'windows', 'mac')
        if config['default']['newline_mode'] not in valid_newline_mode:
            raise ConfigError(
                '[CONFIGERROR] "default:newline_mode" must one of {}'
                .format(valid_newline_mode))

    config = read_config(rootdir)
    config = expand_config(config)
    try:
        check_config(config)
    except ConfigError as e:
        print(e)
        sys.exit(1)
    return config


def register_signal_handler():
    def signal_handler(signal, frame):
        print()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)


def get_rootdir():
    def checkdirs(current_dir):
        paths = [path for path in current_dir.glob('.loli')]
        if len(paths) == 1 and paths[0].is_dir():
            return current_dir
        else:
            if current_dir != current_dir.parent:
                return checkdirs(current_dir.parent)
            else:
                return None

    current_dir = pathlib.Path(os.getcwd())
    return checkdirs(current_dir)


def confirm(message):
    answer = input(message)
    if answer.lower() in ('y', 'yes'):
        return True
    else:
        return False
