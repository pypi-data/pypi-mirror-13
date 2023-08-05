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
        ❏Eupompos❏ eupompos/pyparser.py
        ________________________________________________________________________

        parser for the Python language.
        ________________________________________________________________________

        o PyParser class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import copy
import re

from   eupompos.pyparserstate import PyParserState
from   eupompos.liaf import LIAF
from   eupompos.messages import MSG
from   eupompos.parsertools import FunctionDeclaration
import eupompos.settings as settings
from   eupompos.strtools import remove_final_newlinechars

################################################################################
class PyParser(object):
    """
        PyParser class
        ________________________________________________________________________

        Use this class to parse a C++ file.
        ________________________________________________________________________

        class attributes : -

        instance attribute(s) : -

            o root          : (str) the path to the project's root directory
            o current_liaf  : a LIAF object
            o report        : a ParserReport object (the object to be filled)
            o state         : a PyParserState

        class methods :

            o __init__()
            o parse()
            o add_current_docstring()
            o parse__class_declaration()
            o parse__function_declaration()
            o parse__empty_line()
            o reset()
            o usefull_comment_line()            (static)
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, _report):
        """
                PyParser.__init__()
                ________________________________________________________________

                Set some variables to their default value.
                ________________________________________________________________

                PARAMETERS :

                    o (str)_report     : the ParserReport object to be filled.

                RETURNED VALUE : None
        """
        self.report = _report

        self.root = ""                  # a string
        self.current_liaf = None        # a LIAF object
        self.state = None               # a PyParserState object

    #///////////////////////////////////////////////////////////////////////////
    def parse(self, _root, _filename, _srccontent):
        """
                PyParser.parse()
                ________________________________________________________________

                Parse a file's content and fill self.report.
                ________________________________________________________________

                PARAMETER :
                    o (str)_root       : root path of the project
                    o (str)_filename   : source file's name
                    o (str)_srccontent : the content of the file to be parsed

                RETURNED VALUE : None
        """
        MSG.debug("PyParser.parse : parsing {0}...".format(_filename))

        self.reset()

        self.root = _root

        self.current_liaf.filename = _filename

        for _linenumber, _line in enumerate(_srccontent):

            linenumber = _linenumber+1

            self.current_liaf.linenumber = linenumber
            self.current_liaf.line = _line

            MSG.debug("PyParser.parse() "
                      ": filename={0}; line#{1}={2}".format(self.current_liaf.filename,
                                                            self.current_liaf.linenumber,
                                                            self.current_liaf.line))

            if re.search(settings.REGEX__PYTHON_DOCSTRING,
                         self.current_liaf.line) is not None:
                self.parse__docstring_line()

            elif self.state.inside_docstring:
                self.state.current_block_of_docstrings.lines.append(\
                                remove_final_newlinechars(_line))

            elif re.search(settings.REGEX__PYTHON_CLASSDECLARATION,
                           self.current_liaf.line) is not None:
                self.parse__class_declaration()

            # about function declaration :
            #
            # o   REGEX__FUNCTIONDECLARATION
            # o   no ";" at the end of the line
            # o   no space at the beginning of _line
            #
            elif re.search(settings.REGEX__PYTHON_FUNCTIONDECLARATION,
                           self.current_liaf.line) is not None:
                self.parse__function_declaration()

    #///////////////////////////////////////////////////////////////////////////
    #
    # parse__* functions
    #
    #   These functions return nothing and take no parameter.
    #
    #///////////////////////////////////////////////////////////////////////////

    #...........................................................................
    def parse__class_declaration(self):
        """
                PyParser.parse__class_declaration()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a class declaration.
        """
        MSG.debug("PyParser.parse__class_declaration()")
        self.state.current_class = re.search(settings.REGEX__PYTHON_CLASSDECLARATION,
                                             self.current_liaf.line).group(1)
        self.state.current_function = FunctionDeclaration()
    #...........................................................................
    def parse__docstring_line(self):
        """
                PyParser.parse__docstring_line(self)
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a docstring line.
        """
        MSG.debug("PyParser.parse__docstring_line()")
        line = self.current_liaf.line[:-1]
        line = line.strip()

        self.state.current_block_of_docstrings.lines.append(line)

        if not self.state.inside_docstring:
            # first line of the docstring :
            self.state.current_block_of_docstrings.liaf = copy.copy(self.current_liaf)

        if re.search(settings.REGEX__PYTHON_DOCSTRING_UL, line) is not None:
            # the line is a one-line docstring :
            self.state.inside_docstring = False
        else:
            self.state.inside_docstring = not self.state.inside_docstring

        if not self.state.inside_docstring:
            # the current line was the last one :

            # is there a function defined before the docstring ?
            if self.state.current_function.is_defined():
                # yes, there's a function : but is this function defined just before the
                # current docstring ?
                if self.state.current_function.liaf.linenumber == \
                   self.state.current_block_of_docstrings.liaf.linenumber-1:

                    self.report.add_function(self.state.current_function,
                                             self.state.current_block_of_docstrings.lines,
                                             self.usefull_comment_line)

    #...........................................................................
    def parse__function_declaration(self):
        """
                PyParser.parse__function_declaration()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a function declaration.
        """
        MSG.debug("PyParser.parse__function_declaration()")

        func_name = re.search(settings.REGEX__PYTHON_FUNCTIONDECLARATION,
                              self.current_liaf.line).group(1)

        # if the line doesn't start with a space, it means that it's not a class method :
        if not(self.current_liaf.line.startswith(" ") or self.current_liaf.line.startswith("\b")):
            self.state.current_class = None

        module_name = \
            self.current_liaf.filename[-(len(self.current_liaf.filename)-len(self.root))+1:]
        self.state.current_function = FunctionDeclaration(module_name,
                                                          self.state.current_class,
                                                          func_name,
                                                          copy.copy(self.current_liaf))

        self.state.current_block_of_docstrings.clear()

    #...........................................................................
    def parse__empty_line(self):
        """
                PyParser.parse__empty_line()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads an empty line.
        """
        MSG.debug("PyParser.parse__empty_line()")
        self.state.current_block_of_docstrings.clear()
        self.state.current_class = None

    #///////////////////////////////////////////////////////////////////////////
    def reset(self):
        """
                PyParser.reset()
                ________________________________________________________________

                Reset the attributes specific to a file.
                ________________________________________________________________

                PARAMETER(S) :  no parameter

                RETURNED VALUE :  no RETURNED VALUE
        """
        MSG.debug("PyParser.reset()")
        self.root = ""
        self.current_liaf = LIAF()
        self.state = PyParserState()

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def usefull_comment_line(_line):
        """
                PyParser.usefull_comment_line()
                ________________________________________________________________

                Return True if _line is a usefull line of comment.
                ________________________________________________________________

                PARAMETER :
                    o _line : (str)

                RETURNED VALUE : the expected boolean
        """
        return re.match(settings.REGEX__PYTHON_USEFULLCOM, _line) is not None
