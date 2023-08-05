# Copyright (c) 2000-2013 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
"""
unittest for visitors.diadefs and extensions.diadefslib modules
"""


import os
import sys
import codecs
from os.path import join, dirname, abspath
from difflib import unified_diff
import unittest

from astroid import MANAGER

from pylint.pyreverse.inspector import Linker, project_from_files
from pylint.pyreverse.diadefslib import DefaultDiadefGenerator, DiadefsHandler
from pylint.pyreverse.writer import DotWriter
from pylint.pyreverse.utils import get_visibility


_DEFAULTS = {
    'all_ancestors': None, 'show_associated': None,
    'module_names': None,
    'output_format': 'dot', 'diadefs_file': None, 'quiet': 0,
    'show_ancestors': None, 'classes': (), 'all_associated': None,
    'mode': 'PUB_ONLY', 'show_builtin': False, 'only_classnames': False
    }

class Config(object):
    """config object for tests"""
    def __init__(self):
        for attr, value in _DEFAULTS.items():
            setattr(self, attr, value)


def _file_lines(path):
    # we don't care about the actual encoding, but python3 forces us to pick one
    with codecs.open(path, encoding='latin1') as stream:
        lines = [line.strip() for line in stream.readlines()
                 if (line.find('squeleton generated by ') == -1 and
                     not line.startswith('__revision__ = "$Id:'))]
    return [line for line in lines if line]

def get_project(module, name="No Name"):
    """return a astroid project representation"""
    def _astroid_wrapper(func, modname):
        return func(modname)
    return project_from_files([module], _astroid_wrapper,
                              project_name=name)

CONFIG = Config()

class DotWriterTC(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        project = get_project(os.path.join(os.path.dirname(__file__), 'data'))
        linker = Linker(project)
        handler = DiadefsHandler(CONFIG)
        dd = DefaultDiadefGenerator(linker, handler).visit(project)
        for diagram in dd:
            diagram.extract_relationships()
        writer = DotWriter(CONFIG)
        writer.write(dd)

    @classmethod
    def tearDownClass(cls):
        for fname in ('packages_No_Name.dot', 'classes_No_Name.dot',):
            try:
                os.remove(fname)
            except:
                continue

    def _test_same_file(self, generated_file):
        expected_file = os.path.join(os.path.dirname(__file__), 'data', generated_file)
        generated = _file_lines(generated_file)
        expected = _file_lines(expected_file)
        generated = '\n'.join(generated)
        expected = '\n'.join(expected)
        files = "\n *** expected : %s, generated : %s \n"  % (
            expected_file, generated_file)
        self.assertEqual(expected, generated, '%s%s' % (
            files, '\n'.join(line for line in unified_diff(
            expected.splitlines(), generated.splitlines() ))) )
        os.remove(generated_file)

    def test_package_diagram(self):
        self._test_same_file('packages_No_Name.dot')

    def test_class_diagram(self):
        self._test_same_file('classes_No_Name.dot')



class GetVisibilityTC(unittest.TestCase):

    def test_special(self):
        for name in ["__reduce_ex__",  "__setattr__"]:
            self.assertEqual(get_visibility(name), 'special')

    def test_private(self):
        for name in ["__g_", "____dsf", "__23_9"]:
            got = get_visibility(name)
            self.assertEqual(got, 'private',
                             'got %s instead of private for value %s' % (got, name))

    def test_public(self):
        self.assertEqual(get_visibility('simple'), 'public')

    def test_protected(self):
        for name in ["_","__", "___", "____", "_____", "___e__",
                     "_nextsimple", "_filter_it_"]:
            got = get_visibility(name)
            self.assertEqual(got, 'protected',
                             'got %s instead of protected for value %s' % (got, name))


if __name__ == '__main__':
    unittest.main()
