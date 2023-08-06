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
import textwrap
import sys

from .. import command
from .. import defaultconfig


class HelpCommand(command.Command):
    def get_name(self):
        return 'help'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='show help messages about rules & setting detail. etc.',
            description='show help messages about rules & setting detail.'
                        ' etc.')

        parser.add_argument(
            '--rules', dest='rules', action='store_true',
            help='show lolinote ruleset.')

        parser.add_argument(
            '--config', dest='config', action='store_true',
            help='show how to configure lolikit and current setting values.')

        self.parser = parser

    def run(self, args):
        if len(sys.argv) == 2:
            self.parser.print_help()
            sys.exit(1)
        elif args.rules:
            self.show_rules()
        elif args.config:
            self.show_config()

    def show_rules(self):
        message = textwrap.dedent("""\
            # Loli's Rules #

            1. One note. One file. Every notes are INDEPENDENTLY.
            2. Note files are MARKDOWN format.
            3. Note's filename equiv to "title + .md".
            4. All notes in a multi-level directory tree.
            5. Note's order is the filename string order.
            6. Root folder should have a directory which be named as ".loli".
            7. Note content must encoding as "utf8".

            Check https://bitbucket.org/civalin/lolinote for more detail.""")
        print(message)

    def show_config(self):
        message = textwrap.dedent("""\
            # Lolikit Configuration #

            ## Basic ##

            Lolikit have 3 level settings files.

            - default - in lolikit source code "defaultconfig.py" file.
            - user    - in "~/.lolikitrc".
            - project - in "project/.loli/lolikitrc"

            The default setting will be overwrited by user's setting, and
            user's setting will be overwrited by project's setting.



            ## Configuration Format ##

            The lolikitrc files is a kind of "ini" format. It look like...

                [default]
                show_reverse = on       # This is comment
                ignore_patterns = .swp$ # allow multi-line values
                                  ~$
                [fix]
                small_size = 80



            ## Variables ##

            ### [default] section ###

            #### editor ####

            Some lolikit command may use a editor. This setting
            define which editor should be used (by default).

            example:
                vim

            - default: "{default[default][editor]}"
            - current: "{current[default][editor]}"

            #### file_browser ####

            Some lolikit command may use a file browser. This setting
            define which file browser should be used (by default).

            example:
                nautilus

            - default: "{default[default][file_browser]}"
            - current: "{current[default][file_browser]}"

            #### show_reverse ####

            Some lolikit command will show a list of notes. This setting
            define the list should be reversed or not.

            - default: {default[default][show_reverse]}
            - current: {current[default][show_reverse]}

            #### page_size ####

            Some lolikit command will show a list of notes. This setting
            define how much notes in one page.

            - default: {default[default][page_size]}
            - current: {current[default][page_size]}

            #### ignore_patterns ####

            Determine Which path will be ignore by lonokit.
            It is a list of regex patterns and splitted by lines.

            The "^.loli" pattern will be appended automatically and cannot
            be removed.

            - default: {default[default][ignore_patterns]}
            - current: {current[default][ignore_patterns]}

            #### newline_mode ####

            Define which newline mode should be used in note files.

            available mode:
                - posix
                - windows
                - mac

            - default: "{default[default][newline_mode]}"
            - current: "{current[default][newline_mode]}"



            ### [find] section ###

            #### output_format ####

            Define the output format with "find" command.

            - default: "{default[find][output_format]}"
            - current: "{current[find][output_format]}"



            ### [list] section ###

            #### output_format ####

            Define the output format with "list" command.

            - default: "{default[list][output_format]}"
            - current: "{current[list][output_format]}"



            ### [fix] section ###

            #### danger_pathname_chars ####

            Define what chars is danger in pathname.

            - default: "{default[fix][danger_pathname_chars]}"
            - current: "{current[fix][danger_pathname_chars]}"

            #### danger_pathname_chars_fix_to ####

            Set which char will be used to replace the danger chars when
            fixing.

            - default: "{default[fix][danger_pathname_chars_fix_to]}"
            - current: "{current[fix][danger_pathname_chars_fix_to]}"
            """).format(
            default=defaultconfig.DEFAULT_CONFIG, current=self.config)
        print(message)
