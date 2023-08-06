#!/usr/bin/env python
"""sorno_attach_realdate.py attaches the actual time in human readable format
for timestamps found in coming lines.

Example:

    $ cat /tmp/abc
    once upon a time 1455225387 there is
    1455225387 something called blah
    and 1455225387
    then foo

    $ cat /tmp/abc |python scripts/sorno_attach_realdate.py
    once upon a time 1455225387(2016-02-11 13:16:27) there is
    1455225387(2016-02-11 13:16:27) something called blah
    and 1455225387(2016-02-11 13:16:27)
    then foo


    Copyright 2016 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
import fileinput
import sys

from sorno import datetimeutil


_datetime_format = "%Y-%m-%d %H:%M:%S"


class App(object):
    def __init__(self, args):
        self.args = args

    def run(self):
        for line in fileinput.input():
            sys.stdout.write(self._process(line))
        return 0

    def _process(self, line):
        return datetimeutil.TIMESTAMP_REGEX.sub(self._repl, line)

    def _repl(self, match):
        potential_ts = match.group()
        num = int(potential_ts)
        try:
            dt, unit = datetimeutil.number_to_local_datetime(num)
        except ValueError:
            return potential_ts

        return "%s(%s)" % (potential_ts, dt.strftime(_datetime_format))


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2016")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    app = App(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
