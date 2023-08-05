import re

from coalib.bearlib.abstractions.Lint import Lint
from coalib.bears.LocalBear import LocalBear
from coalib.settings.Setting import typed_list


class CPPLintBear(LocalBear, Lint):
    executable = 'cpplint'
    output_regex = re.compile(
        r'(?P<filename>.+\..+):(?P<line>\d+):\s(?P<message>.+)')
    use_stderr = True

    def run(self,
            filename,
            file,
            cpplint_ignore: typed_list(str)=[],
            cpplint_include: typed_list(str)=[]):
        '''
        Checks the code with `cpplint` on each file separately.

        :param cpplint_ignore:  List of checkers to ignore.
        :param cpplint_include: List of checkers to explicitly enable.
        '''
        ignore = ','.join('-'+part.strip() for part in cpplint_ignore)
        include = ','.join('+'+part.strip() for part in cpplint_include)
        self.arguments = '--filter=' + ignore + ',' + include
        return self.lint(filename)
