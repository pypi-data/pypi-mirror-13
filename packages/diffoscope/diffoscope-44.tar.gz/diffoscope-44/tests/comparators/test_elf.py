# -*- coding: utf-8 -*-
#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015 Jérémy Bobbio <lunar@debian.org>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import pytest
from diffoscope.comparators import specialize
from diffoscope.comparators.binary import FilesystemFile, NonExistingFile
from diffoscope.comparators.elf import ElfFile, StaticLibFile
from diffoscope.config import Config
from conftest import tool_missing

TEST_OBJ1_PATH = os.path.join(os.path.dirname(__file__), '../data/test1.o')
TEST_OBJ2_PATH = os.path.join(os.path.dirname(__file__), '../data/test2.o')

@pytest.fixture
def obj1():
    return specialize(FilesystemFile(TEST_OBJ1_PATH))

@pytest.fixture
def obj2():
    return specialize(FilesystemFile(TEST_OBJ2_PATH))

def test_obj_identification(obj1):
    assert isinstance(obj1, ElfFile)

def test_obj_no_differences(obj1):
    difference = obj1.compare(obj1)
    assert difference is None

@pytest.fixture
def obj_differences(obj1, obj2):
    return obj1.compare(obj2).details

@pytest.mark.skipif(tool_missing('readelf'), reason='missing readelf')
def test_obj_compare_non_existing(monkeypatch, obj1):
    monkeypatch.setattr(Config, 'new_file', True)
    difference = obj1.compare(NonExistingFile('/nonexisting', obj1))
    assert difference.source2 == '/nonexisting'

@pytest.mark.skipif(tool_missing('readelf'), reason='missing readelf')
def test_diff(obj_differences):
    assert len(obj_differences) == 1
    expected_diff = open(os.path.join(os.path.dirname(__file__), '../data/elf_obj_expected_diff')).read()
    assert obj_differences[0].unified_diff == expected_diff

TEST_LIB1_PATH = os.path.join(os.path.dirname(__file__), '../data/test1.a')
TEST_LIB2_PATH = os.path.join(os.path.dirname(__file__), '../data/test2.a')

@pytest.fixture
def lib1():
    return specialize(FilesystemFile(TEST_LIB1_PATH))

@pytest.fixture
def lib2():
    return specialize(FilesystemFile(TEST_LIB2_PATH))

def test_lib_identification(lib1):
    assert isinstance(lib1, StaticLibFile)

def test_lib_no_differences(lib1):
    difference = lib1.compare(lib1)
    assert difference is None

@pytest.fixture
def lib_differences(lib1, lib2):
    return lib1.compare(lib2).details

@pytest.mark.skipif(tool_missing('readelf'), reason='missing readelf')
def test_lib_differences(lib_differences):
    assert len(lib_differences) == 2
    assert lib_differences[0].source1 == 'metadata'
    expected_metadata_diff = open(os.path.join(os.path.dirname(__file__), '../data/elf_lib_metadata_expected_diff')).read()
    assert lib_differences[0].unified_diff == expected_metadata_diff
    assert 'objdump' in lib_differences[1].source1
    expected_objdump_diff = open(os.path.join(os.path.dirname(__file__), '../data/elf_lib_objdump_expected_diff')).read()
    assert lib_differences[1].unified_diff == expected_objdump_diff

@pytest.mark.skipif(tool_missing('readelf'), reason='missing readelf')
def test_lib_compare_non_existing(monkeypatch, lib1):
    monkeypatch.setattr(Config, 'new_file', True)
    difference = lib1.compare(NonExistingFile('/nonexisting', lib1))
    assert difference.source2 == '/nonexisting'
