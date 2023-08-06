# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json

from coalib.output.printers.ListLogPrinter import ListLogPrinter
from coalib.output.JSONEncoder import JSONEncoder
from coalib.coala_main import run_coala
from coalib.misc.Exceptions import get_exitcode
from coalib.parsing.DefaultArgParser import default_arg_parser


def main():
    # Note: We parse the args here once to find the log printer to use.
    #       Also, commands like -h (help) and -v (version) are executed here.
    #       The args are again parsed later to find the settings and configs
    #       to use during analysis.
    arg_parser = default_arg_parser()
    try:
        args = arg_parser.parse_args()
    except BaseException as exception:  # Ignore PyLintBear
        return get_exitcode(exception)

    log_printer = None if args.text_logs else ListLogPrinter()
    results, exitcode = run_coala(log_printer=log_printer, autoapply=False)

    retval = {"results": results}
    if not args.text_logs:
        retval["logs"] = log_printer.logs

    print(json.dumps(retval,
                     cls=JSONEncoder,
                     sort_keys=True,
                     indent=2,
                     separators=(',', ': ')))

    return exitcode
