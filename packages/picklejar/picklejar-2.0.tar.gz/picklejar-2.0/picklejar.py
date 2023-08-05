# coding=utf-8
"""PickleJar is a python module that allows you to work with multiple pickles while reading/writing 
them to a single file/jar.
"""
# Copyright (C) 2015 Jesse Almanrode
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Imports
import os
import dill


class Jar(object):
    """A file containing multiple pickle objects

    :param filepath: Path to the file
    :param always_list: Ensure that Jars with single pickle return as a list (default = False)
    :return: Jar object
    """
    def __init__(self, filepath, always_list=False):
        filepath = os.path.abspath(os.path.expanduser(filepath))
        self.jar = os.path.abspath(filepath)
        self.always_list = always_list

    def exists(self):
        """Does the Jar exist

        :return: True or False
        """
        if os.path.exists(self.jar):
            return True
        else:
            return False

    def remove(self):
        """Remove the current jar file if it exists

        :return: True if jar file was removed, False otherwise
        """
        if self.exists():
            os.remove(self.jar)
            return True
        else:
            return False

    def load(self, always_list=False):
        """Loads all the pickles out of the file/jar

        :param always_list: Ensure that Jars with single pickle return as a list (default = False)
        :return: List of de-pickled objects
        """
        _pickles = []
        _jar = open(self.jar, 'rb')
        while True:
            try:
                _pickles.append(dill.load(_jar))
            except EOFError:
                break
        _jar.close()
        if len(_pickles) == 1:
            if self.always_list or always_list:
                return _pickles
            else:
                return _pickles[0]
        else:
            return _pickles

    def dump(self, pickles, newjar=False, collapse=False):
        """Write a Pickle to the file/jar.

        :param pickles: Item or list of items to pickle
        :param newjar: Start a new jar (default = False)
        :param collapse: If pickles is a list write list as single pickle
        :return: True on file write
        """
        if newjar:
            _jar = open(self.jar, 'wb')
        else:
            _jar = open(self.jar, 'ab')
        if collapse:
            dill.dump(pickles, _jar, dill.HIGHEST_PROTOCOL)
        else:
            if type(pickles) is list:
                for pkle in pickles:
                    dill.dump(pkle, _jar, dill.HIGHEST_PROTOCOL)
            else:
                dill.dump(pickles, _jar, dill.HIGHEST_PROTOCOL)
        _jar.close()
        return True

