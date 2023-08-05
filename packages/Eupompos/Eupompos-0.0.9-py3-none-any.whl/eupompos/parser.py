#!/usr/bin/python
# -*- coding: utf-8 -*-
################################################################################
#    Eupompos Copyright (C) 2012 Xavier Faure
#    Contact: suizozukan arrobas orange dot fr
#
#    This file is part of Eupompos.
#    Eupompos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Eupompos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Eupompos.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
"""
        ❏Eupompos❏ eupompos/parser.py
        ________________________________________________________________________

        parser for all the known languages.
        ________________________________________________________________________

        o Parser class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import os.path
import re

from eupompos.cppparser import CppParser
from eupompos.pyparser import PyParser
from eupompos.filetools import normpath
from eupompos.messages import MSG
from eupompos.parserreport import ParserReport
import eupompos.settings as settings

################################################################################
class Parser(object):
    """
        Parser class
        ________________________________________________________________________

        Use this class to parse a path or a file.
        ________________________________________________________________________

        class attributes : -

        instance attribute(s) : -

            o cppparser : a CppParser object
            o report    : a ParserReport object

        class methods :

            o __init__()
            o filename_ok()     [static]
            o parse_a_file()
            o parse_a_path()
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, _src):
        """
                Parser.__init__()
                ________________________________________________________________

                Entry point of the class : lauch the parsing of the source named
                _src.
                ________________________________________________________________

                PARAMETER :
                    o (str)_src : either a path either a file

                RETURNED VALUE : None
        """
        self.report = ParserReport()

        self.cppparser = CppParser(self.report)
        self.pyparser = PyParser(self.report)

        source = normpath(_src)

        if not os.path.exists(source):
            MSG.error("The path \"{0}\" (full path : \"{1}\") doesn't exist.".format(_src, source))

        elif os.path.isfile(source):
            self.parse_a_file(_src, *os.path.split(source))

        elif os.path.isdir(source):
            self.parse_a_path(source)

        else:
            MSG.error("\"{0}\" (full path : \"{1}\") is " \
                      "neither a file nor a directory.".format(_src,
                                                               source))

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def filename_ok(_path, _filename):
        """
                Parser.filename_ok()
                ________________________________________________________________

                Say if the file named "_path,_filename" has to be parsed.
                ________________________________________________________________

                PARAMETERS :
                    o (str) _path               : path to the file
                    o (str) _filename           : filename (without the path)

                RETURNED VALUE : ( (bool)ok, (None/str)language )

                        language : either None, either "python", either "cpp"
        """
        res = (False, None)

        if re.search(settings.REGEX__PYTHON_FILENAMES, _filename) is not None:
            res = (True, "python")

        elif re.search(settings.REGEX__CPP_CODE_FILENAMES, _filename) is not None:
            res = (True, "cpp")

        for keyword in settings.FULLNAME_BLACKLIST:
            if keyword in _path or keyword in _filename:
                res = (False, None)
                break

        return res

    #///////////////////////////////////////////////////////////////////////////
    def parse_a_file(self, _projectsource, _root, _filename):
        """
                Parser.parse_a_file()
                ________________________________________________________________

                Parse the file named _root+_filename.
                ________________________________________________________________

                PARAMETER :
                    o (str) _projectsource, the project's source directory
                    o (str) _root, the file's directory
                    o (str) _filename, the file's name.

                RETURNED VALUE : None
        """
        MSG.debug("Parser.parse_a_file() : {0}, {1}, {2}".format(_projectsource, _root, _filename))

        tobeparsed, language = Parser.filename_ok(_root, _filename)

        if tobeparsed:
            with open(os.path.join(_root, _filename), 'r') as src:

                if language == "cpp":
                    self.cppparser.parse(_filename=os.path.join(_root, _filename),
                                         _srccontent=src)

                elif language == "python":
                    self.pyparser.parse(_root=_projectsource,
                                        _filename=os.path.join(_root, _filename),
                                        _srccontent=src)

    #///////////////////////////////////////////////////////////////////////////
    def parse_a_path(self, _src):
        """
                Parser.parse_a_path()
                ________________________________________________________________

                Parse the directory named _src.
                ________________________________________________________________

                PARAMETER :
                    o (str)_src : the directory's name

                RETURNED VALUE : None
        """
        MSG.debug("Parser.parse_a_path() : " + _src)

        self.report.clear()

        for root, _, files in os.walk(_src):
            for filename in files:
                self.parse_a_file(_src, root, filename)

