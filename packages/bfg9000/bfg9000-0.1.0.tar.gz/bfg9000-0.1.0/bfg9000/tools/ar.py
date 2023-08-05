import os

from .. import shell
from .. import file_types
from .. import iterutils
from ..path import Root


class ArLinker(object):
    rule_name = command_var = link_var = 'ar'

    def __init__(self, env, lang):
        self.platform = env.platform
        self.mode = 'static_library'
        self.lang = lang

        self.command = env.getvar('AR', 'ar')
        self.global_args = shell.split(env.getvar('ARFLAGS', 'cru'))

    @property
    def flavor(self):
        return 'ar'

    def __call__(self, cmd, input, output, args=None):
        result = [cmd]
        result.extend(iterutils.iterate(args))
        result.append(output)
        result.extend(iterutils.iterate(input))
        return result

    def output_file(self, name):
        head, tail = os.path.split(name)
        path = os.path.join(head, 'lib' + tail + '.a')
        return file_types.StaticLibrary(path, Root.builddir, self.lang)

    @property
    def mode_args(self):
        return []
