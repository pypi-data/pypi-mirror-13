import os.path
from enum import Enum
from itertools import chain

from . import safe_str

Root = Enum('Root', ['srcdir', 'builddir', 'absolute'])
InstallRoot = Enum('InstallRoot', ['prefix', 'bindir', 'libdir', 'includedir'])


class Path(safe_str.safe_string):
    def __init__(self, path, root=Root.builddir):
        self.suffix = os.path.normpath(path)
        if self.suffix == '.':
            self.suffix = ''

        if os.path.isabs(path):
            self.root = Root.absolute
        elif root == Root.absolute:
            raise ValueError("'{}' is not absolute".format(path))
        else:
            self.root = root

    def parent(self):
        if not self.suffix:
            raise ValueError('already at root')
        return Path(os.path.dirname(self.suffix), self.root)

    def append(self, path):
        return Path(os.path.join(self.suffix, path), self.root)

    def addext(self, ext):
        return Path(self.suffix + ext, self.root)

    def basename(self):
        return os.path.basename(self.suffix)

    def relpath(self, start):
        if os.path.isabs(self.suffix):
            return self.suffix
        else:
            if self.root != start.root:
                raise ValueError('source mismatch')
            return os.path.relpath(self.suffix or '.', start.suffix or '.')

    def to_json(self):
        return (self.suffix, self.root.name)

    @staticmethod
    def from_json(data):
        try:
            base = Root[data[1]]
        except:
            base = InstallRoot[data[1]]
        return Path(data[0], base)

    def realize(self, variables, executable=False):
        root = variables[self.root] if self.root != Root.absolute else None
        if executable and root is None and os.path.sep not in self.suffix:
            root = '.'

        if root is None:
            return self.suffix or '.'
        if not self.suffix:
            return root
        return root + os.path.sep + self.suffix

    def string(self):
        return self.realize(None)

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        variables = {i: '$({})'.format(i.name) for i in
                     chain(Root, InstallRoot)}
        return '`{}`'.format(self.realize(variables))

    def __hash__(self):
        return hash(self.suffix)

    def __eq__(self, rhs):
        return self.root == rhs.root and self.suffix == rhs.suffix

    def __nonzero__(self):
        return self.__bool__()

    def __bool__(self):
        return self.root != Root.builddir or bool(self.suffix)

    def __add__(self, rhs):
        return safe_str.jbos(self, rhs)

    def __radd__(self, lhs):
        return safe_str.jbos(lhs, self)


def install_path(path, install_root):
    if path.root == Root.srcdir:
        suffix = os.path.basename(path.suffix)
    else:
        suffix = path.suffix
    return Path(suffix, install_root)
