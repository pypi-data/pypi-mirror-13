import os.path

from .integration import *


class TestFindFiles(IntegrationTest):
    def __init__(self, *args, **kwargs):
        IntegrationTest.__init__(
            self, os.path.join(examples_dir, '06_find_files'), *args, **kwargs
        )

    def test_hello(self):
        self.build(executable('hello'))
        self.assertOutput([executable('hello')], 'Hello, world!\n')

    def test_goodbye(self):
        self.build(executable('goodbye'))
        self.assertOutput([executable('goodbye')],
                          'Goodbye!\nAuf Wiedersehen!\n')
