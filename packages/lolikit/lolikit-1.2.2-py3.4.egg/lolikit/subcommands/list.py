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


import argparse

from .. import command
from .. import notelistselector as NLS


class ListCommand(command.Command):
    def get_name(self):
        return 'list'

    def register_parser(self, subparsers):
        subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='lists some notes that have recently be changed',
            description='lists some notes that have recently be changed\n'
                        'result may not consistent after file copied.')

    def run(self, args):
        self.require_rootdir()

        notes = [NLS.Note(path, self.rootdir)
                 for path in self.get_all_md_paths()]
        notes.sort(key=lambda x: x.path.stat().st_mtime, reverse=True)
        NLS.start_selector(
            notes=notes,
            show_reverse=self.config['default'].getboolean('show_reverse'),
            editor=self.config['default']['editor'],
            file_browser=self.config['default']['file_browser'],
            page_size=int(self.config['default']['page_size']),
            output_format=self.config[self.get_name()]['output_format'])
