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
import re

from .. import command
from .. import notelistselector as NLS


class FindCommand(command.Command):
    def get_name(self):
        return 'find'

    def register_parser(self, subparsers):
        parser = subparsers.add_parser(
            self.get_name(),
            formatter_class=argparse.RawTextHelpFormatter,
            help='find some notes which contain some special pattern',
            description='find aome notes which contain some special pattern')

        parser.add_argument(
            'pattern', metavar='PATTERN', type=str, nargs='+',
            help='string or regex pattern for finding')

        parser.add_argument(
            '-s', metavar='PAGESIZE', dest='page_size', type=int,
            default=int(self.config['default']['page_size']),
            help='override each page\'s items count')

    def run(self, args):
        self.require_rootdir()
        scored_notes = [
            (self.calculate_score(*data),
             NLS.Note(data[0], self.rootdir))
            for data in self.get_all_matches(args.pattern)]
        notes = [note for score, note
                 in sorted(scored_notes, key=lambda x: x[0], reverse=True)]

        if len(notes) > 0:
            NLS.start_selector(
                notes=notes,
                show_reverse=self.config['default'].getboolean('show_reverse'),
                editor=self.config['default']['editor'],
                file_browser=self.config['default']['file_browser'],
                page_size=args.page_size,
                output_format=self.config[self.get_name()]['output_format'])

    def get_all_matches(self, patterns):
        """
        yield: (path, content, title_matches_list, content_matches_list)
        """
        def get_matches(path, progs):
            title_matches_list = [
                tuple(m for m in prog.finditer(path.stem))
                for prog in progs]
            with open(str(path), encoding='utf8') as f:
                content = f.read()
            content_matches_list = [
                tuple(m for m in prog.finditer(content))
                for prog in progs]
            return content, title_matches_list, content_matches_list

        progs = [re.compile(pattern, re.IGNORECASE)
                 for pattern in patterns]
        for path in self.get_all_md_paths():
            (content,
             title_matches_list,
             content_matches_list) = get_matches(path, progs)

            hit = all([any((title_matches, content_matches))
                      for title_matches, content_matches
                      in zip(title_matches_list, content_matches_list)])
            if hit:
                yield (path, content,
                       title_matches_list, content_matches_list)

    def calculate_score(self, path, content,
                        title_matches_list, content_matches_list):
        def get_title_score(title, title_matches_list):
            # title_matches_len = 0
            # for title_matches in title_matches_list:
            #     title_matches_len += len(
            #         ''.join(m.group(0) for m in title_matches))
            # return title_matches_len / len(title)
            return sum(len(tms) for tms in title_matches_list)

        def get_content_score(content, content_matches_list):
            content_matches_len = 0
            for content_matches in content_matches_list:
                content_matches_len += len(
                    ''.join(m.group(0) for m in content_matches))
            return content_matches_len / len(content)

        def get_repeat_score(content_score, content_matches_list):
            repeat_count = 0
            for content_matches in content_matches_list:
                repeat_count += len(content_matches)
            return repeat_count * content_score

        title_score = get_title_score(path.stem, title_matches_list)
        content_score = get_content_score(content, content_matches_list)
        repeat_score = get_repeat_score(content_score, content_matches_list)
        total_score = title_score + content_score + repeat_score
        return total_score
