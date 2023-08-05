"""Integration tests for file IO."""
# pylint: disable=missing-docstring,no-self-use,no-member,misplaced-comparison-constant


import logging

import pytest

import yorm
from yorm.converters import Integer, String, Float, Boolean, Dictionary, List

from . import refresh_file_modification_times


# classes ######################################################################


class EmptyDictionary(Dictionary):

    """Sample dictionary container."""


@yorm.attr(all=Integer)
class IntegerList(List):

    """Sample list container."""


@yorm.attr(object=EmptyDictionary, array=IntegerList, string=String)
@yorm.attr(number_int=Integer, number_real=Float)
@yorm.attr(true=Boolean, false=Boolean)
@yorm.sync("path/to/{self.category}/{self.name}.yml")
class SampleStandardDecorated:

    """Sample class using standard attribute types."""

    def __init__(self, name, category='default'):
        self.name = name
        self.category = category
        # https://docs.python.org/3.4/library/json.html#json.JSONDecoder
        self.object = {}
        self.array = []
        self.string = ""
        self.number_int = 0
        self.number_real = 0.0
        self.true = True
        self.false = False
        self.null = None

    def __repr__(self):
        return "<decorated {}>".format(id(self))


# tests ########################################################################


class TestCreate:

    """Integration tests for creating mapped classes."""

    def test_fetch_from_existing(self, tmpdir):
        """Verify attributes are updated from an existing file."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample2 = SampleStandardDecorated('sample')
        assert sample2.__mapper__.path == sample.__mapper__.path

        refresh_file_modification_times()

        logging.info("changing values in object 1...")
        sample.array = [0, 1, 2]
        sample.string = "Hello, world!"
        sample.number_int = 42
        sample.number_real = 4.2
        sample.true = True
        sample.false = False

        logging.info("reading changed values in object 2...")
        assert [0, 1, 2] == sample2.array
        assert "Hello, world!" == sample2.string
        assert 42 == sample2.number_int
        assert 4.2 == sample2.number_real
        assert True is sample2.true
        assert False is sample2.false


class TestDelete:

    """Integration tests for deleting files."""

    def test_read(self, tmpdir):
        """Verify a deleted file cannot be read from."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample.__mapper__.delete()

        with pytest.raises(FileNotFoundError):
            print(sample.string)

        with pytest.raises(FileNotFoundError):
            sample.string = "def456"

    def test_write(self, tmpdir):
        """Verify a deleted file cannot be written to."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample.__mapper__.delete()

        with pytest.raises(FileNotFoundError):
            sample.string = "def456"

    def test_multiple(self, tmpdir):
        """Verify a deleted file can be deleted again."""
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        sample.__mapper__.delete()
        sample.__mapper__.delete()


class TestUpdate:

    """Integration tests for updating files/object."""

    def test_automatic_store_after_first_modification(self, tmpdir):
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        assert "number_int: 0\n" in sample.__mapper__.text

        sample.number_int = 42
        assert "number_int: 42\n" in sample.__mapper__.text

        sample.__mapper__.text = "number_int: true\n"
        assert 1 is sample.number_int
        assert "number_int: 1\n" in sample.__mapper__.text

    def test_automatic_store_after_first_modification_on_list(self, tmpdir):
        tmpdir.chdir()
        sample = SampleStandardDecorated('sample')
        assert "array: []\n" in sample.__mapper__.text

        sample.array.append(42)
        assert "array:\n- 42\n" in sample.__mapper__.text

        sample.__mapper__.text = "array: [true]\n"
        try:
            iter(sample)
        except AttributeError:
            pass
        assert "array:\n- 1\n" in sample.__mapper__.text
