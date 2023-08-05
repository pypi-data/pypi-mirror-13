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
        ❏Eupompos❏ eupompos/cppparser.py
        ________________________________________________________________________

        parser for the C++ language.
        ________________________________________________________________________

        o CppParser class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import copy
import re

from   eupompos.cppparserstate import CppParserState
from   eupompos.liaf import LIAF
from   eupompos.messages import MSG
from   eupompos.parsertools import FunctionDeclaration
import eupompos.settings as settings

################################################################################
class CppParser(object):
    """
        CppParser class
        ________________________________________________________________________

        Use this class to parse a C++ file.
        ________________________________________________________________________

        class attributes : -

        instance attribute(s) : -

            o current_liaf  : a LIAF object
            o report        : a ParserReport object (the object to be filled)
            o state         : a CppParserState

        class methods :

            o __init__()
            o parse()
            o parse__double_slash_line()
            o parse__function_declaration()
            o parse__empty_line()
            o parse__slash_dot()
            o parse__slash_dot_end()
            o parse__slash_star()
            o reset()
            o usefull_comment_line()            (static)
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, _report):
        """
                CppParser.__init__()
                ________________________________________________________________

                Set some variables to their default value.
                ________________________________________________________________

                PARAMETERS :

                    o (str)_report     : the ParserReport object to be filled.

                RETURNED VALUE : None
        """
        self.report = _report

        self.current_liaf = None        # a LIAF object
        self.state = None               # a CppParserState object

    #///////////////////////////////////////////////////////////////////////////
    def parse(self, _filename, _srccontent):
        """
                CppParser.parse()
                ________________________________________________________________

                Parse a file's content and fill self.report.
                ________________________________________________________________

                PARAMETER :
                    o (str)_filename   : source file's name
                    o (str)_srccontent : the content of the file to be parsed

                RETURNED VALUE : None
        """
        MSG.debug("CppParser.parse : parsing {0}...".format(_filename))

        self.reset()

        self.current_liaf.filename = _filename

        for _linenumber, _line in enumerate(_srccontent):

            linenumber = _linenumber+1

            self.current_liaf.linenumber = linenumber
            self.current_liaf.line = _line.strip()

            MSG.debug("CppParser.parse() "
                      ": filename={0}; line#{1}={2}".format(self.current_liaf.filename,
                                                            self.current_liaf.linenumber,
                                                            self.current_liaf.line))

            if len(self.current_liaf.line) == 0 and not self.state.inside_slashstar:
                self.parse__empty_line()

            elif self.current_liaf.line.startswith("//") and not self.state.inside_slashstar:
                self.parse__double_slash_line()

            elif self.current_liaf.line.startswith("/*"):
                self.parse__slash_dot()

            elif self.current_liaf.line.endswith("*/"):
                self.parse__slash_dot_end()

            elif self.state.inside_slashstar:
                self.parse__slash_star()

##            elif len(self.state.current_connections_line) == 1:
##                self.parse__connect2()

##            elif self.current_liaf.line.startswith("QObject::connect("):
##                # first of two lines :
##                self.state.current_connections_line.append(self.current_liaf.line)

            # about function declaration :
            #
            # o   REGEX__FUNCTIONDECLARATION
            # o   no ";" at the end of the line
            # o   no space at the beginning of _line
            #
            elif re.search(settings.REGEX__CPP_FUNCTIONDECLARATION,
                           self.current_liaf.line) is not None and \
                 not self.current_liaf.line.endswith(";") and \
                 _line.lstrip() == _line:

                self.parse__function_declaration()

##            elif self.current_liaf.line.startswith('emit '):
##                self.parse__emit()

            else:
                # whatever was the line, it wasn't a comment. So we may
                # consider this line not being a part of the preceding block
                # of comments.
                self.state.current_block_of_comments.clear()

    #///////////////////////////////////////////////////////////////////////////
    #
    # parse__* functions
    #
    #   These functions return nothing and take no parameter.
    #
    #///////////////////////////////////////////////////////////////////////////

    #...........................................................................
    def parse__double_slash_line(self):
        """
                CppParser.parse__double_slash_line()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a comment beginning with //
        """
        MSG.debug("CppParser.parse__double_slash_line()")
        line = self.current_liaf.line[2:]
        line = line.strip()
        self.state.current_block_of_comments.append(line)

    #...........................................................................
    def parse__function_declaration(self):
        """
                CppParser.parse__function_declaration()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a function declaration.
        """
        MSG.debug("CppParser.parse__function_declaration()")

        # getting all the groups matching REGEX__CPP_FUNCTIONDECLARATION :
        #
        # e.g. for a regex like :
        #     function declaration = ([_a-zA-Z]+::[_a-zA-Z]+)\(|int\s+(main)\(
        #
        #     ->
        #
        #         (None, 'main') for "int main(...)"
        #      or ('AA', 'BB') for "void AA:BB(...)"
        func_name_groups = re.search(settings.REGEX__CPP_FUNCTIONDECLARATION,
                                     self.current_liaf.line).groups()

        # getting the only element of func_name_groups to be different from None :
        func_name = [fn for fn in func_name_groups if fn is not None][-1]

        self.state.current_function = FunctionDeclaration().init_from_str(func_name, "cpp")
        self.state.current_function.liaf = copy.copy(self.current_liaf)

        self.report.add_function(self.state.current_function,
                                 self.state.current_block_of_comments,
                                 self.usefull_comment_line)

        self.state.current_block_of_comments.clear()

    #...........................................................................
    def parse__empty_line(self):
        """
                CppParser.parse__empty_line()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads an empty line.
        """
        MSG.debug("CppParser.parse__empty_line()")
        self.state.current_block_of_comments.clear()

    #...........................................................................
    def parse__slash_dot(self):
        """
                CppParser.parse__slash_dot()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a ligne beginning with /* .
        """
        MSG.debug("CppParser.parse__slash_dot()")
        line = self.current_liaf.line[2:]
        line = line.strip()
        self.state.inside_slashstar = True
        if len(line) > 0:
            self.state.current_block_of_comments.append(line)

    #...........................................................................
    def parse__slash_dot_end(self):
        """
                CppParser.parse__slash_dot_end()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a ligne ending with */
        """
        MSG.debug("CppParser.parse__slash_dot_end()")
        line = self.current_liaf.line[2:]
        line = line.strip()
        self.state.inside_slashstar = False

        if len(line) > 0:
            self.state.current_block_of_comments.append(line)

    #...........................................................................
    def parse__slash_star(self):
        """
                CppParser.parse__slash_star()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a line inside a /* ... */
                structure .
        """
        MSG.debug("CppParser.parse__slash_star()")
        if len(self.current_liaf.line):
            self.state.current_block_of_comments.append(self.current_liaf.line)

    #///////////////////////////////////////////////////////////////////////////
    def reset(self):
        """
                CppParser.reset()
                ________________________________________________________________

                Reset the attributes specific to a file.
                ________________________________________________________________

                PARAMETER(S) :  no parameter

                RETURNED VALUE :  no RETURNED VALUE
        """
        MSG.debug("CppParser.reset()")
        self.current_liaf = LIAF()
        self.state = CppParserState()

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def usefull_comment_line(_line):
        """
                CppParser.usefull_comment_line()
                ________________________________________________________________

                Return True if _line is a usefull line of comment.
                ________________________________________________________________

                PARAMETER :
                    o _line : (str)

                RETURNED VALUE : the expected boolean
        """
        return re.match(settings.REGEX__CPP_USEFULLCOM, _line) is not None
