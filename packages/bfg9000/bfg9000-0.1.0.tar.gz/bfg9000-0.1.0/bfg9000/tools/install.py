from .hooks import tool


@tool('install')
class Install(object):
    rule_name = command_var = 'install'

    def __init__(self, env):
        default = 'ginstall' if env.platform.name == 'darwin' else 'install'
        self.command = env.getvar('INSTALL', default)

    @property
    def data_args(self):
        return ['-m', '644']

    def __call__(self, cmd, src, dst):
        return [cmd, '-D', src, dst]
