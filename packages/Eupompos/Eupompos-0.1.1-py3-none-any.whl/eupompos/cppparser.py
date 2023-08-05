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

import re

from   eupompos.cppparserstate import CppParserState
from   eupompos.liaf import LLIAF
from   eupompos.messages import MSG
from   eupompos.cppfuncdecl import FunctionDeclaration
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

            o current_lliaf : a LLIAF object
            o root          : (str) project's root directory
            o report        : a ParserReport object (the object to be filled)
            o state         : a CppParserState

        class methods :

            o __init__()
            o parse()
            o parse__double_slash_line()
            o parse__func_declaration_end()
            o parse__func_declaration_start()
            o parse__empty_line()
            o parse__preprocessorif()
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

        self.current_lliaf = None       # a LLIAF object
        self.state = None               # a CppParserState object

        self.root = ""

        self.reset()

    #///////////////////////////////////////////////////////////////////////////
    def parse(self, _root, _filename, _srccontent):
        """
                CppParser.parse()
                ________________________________________________________________

                Parse a file's content and fill self.report.
                ________________________________________________________________

                PARAMETER :
                    o (str)_root       : project's root directory
                    o (str)_filename   : source file's name
                    o (str)_srccontent : the content of the file to be parsed

                RETURNED VALUE : None
        """
        MSG.debug("CppParser.parse() : parsing {0}...".format(_filename))
        self.reset()

        self.root = _root

        self.current_lliaf.filename = _filename

        for _linenumber, _line in enumerate(_srccontent):

            linenumber = _linenumber+1

            self.current_lliaf.firstlinenumber = linenumber
            self.current_lliaf.lines = _line.strip()

            MSG.debug("CppParser.parse() "
                      ": filename={0}; lines#{1}=\"{2}\"".format(self.current_lliaf.filename,
                                                                 self.current_lliaf.firstlinenumber,
                                                                 self.current_lliaf.lines))

            if len(self.current_lliaf.lines) == 0 and not self.state.inside_slashstar:
                self.parse__empty_line()

            elif self.current_lliaf.lines.startswith("//") and not self.state.inside_slashstar:
                self.parse__double_slash_line()

            elif self.current_lliaf.lines.startswith("/*"):
                self.parse__slash_dot()

            elif self.current_lliaf.lines.endswith("*/"):
                self.parse__slash_dot_end()

            elif self.state.inside_slashstar:
                self.parse__slash_star()

            elif self.state.inside_funcdecl:
                self.state.current_funcdecl.data.lines.append(self.current_lliaf.lines)

                self.state.inside_funcdecl = "{" not in self.current_lliaf.lines

                if not self.state.inside_funcdecl:
                    self.parse__func_declaration_end()

            elif self.current_lliaf.lines.startswith(("#if", "#elif", "#ifdef",
                                                      "#ifndef", "#else", "#endif")):
                self.parse__preprocessorif()

            # about function declaration :
            #
            # o   REGEX__FUNCTIONDECLARATION
            # o   no ";" at the end of the line
            # o   no space at the beginning of _line
            # o   no "#define" at the beginning of the line
            #
            elif re.search(settings.REGEX__CPP_FUNCTIONDECLARATIONFIRSTLINE,
                           self.current_lliaf.lines) is not None and \
                 not self.current_lliaf.lines.endswith(";") and \
                 _line.lstrip() == _line and \
                 not _line.lstrip().startswith("#define"):

                self.parse__func_declaration_start()

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
        line = self.current_lliaf.lines[2:]
        line = line.strip()
        self.state.current_block_of_comments.append(line)

    #...........................................................................
    def parse__func_declaration_end(self):
        """
                CppParser.parse__func_declaration_end()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads the end of a function declaration.
        """
        MSG.debug("CppParser.parse__func_declaration_end()")

        self.state.current_funcdecl.init_from_data(self.state.preprocessorif)

        self.report.add_function(self.state.current_funcdecl,
                                 self.state.current_block_of_comments,
                                 self.usefull_comment_line)

    #...........................................................................
    def parse__func_declaration_start(self):
        """
                CppParser.parse__func_declaration_start()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a function declaration.
        """
        MSG.debug("CppParser.parse__func_declaration_start()")

        self.state.current_funcdecl = FunctionDeclaration()
        self.state.current_funcdecl.data = \
                            LLIAF(_filename=self.current_lliaf.filename[len(self.root)+1:],
                                  _firstlinenumber=self.current_lliaf.firstlinenumber,
                                  _lines=[self.current_lliaf.lines,])

        self.state.inside_funcdecl = "{" not in self.current_lliaf.lines

        if not self.state.inside_funcdecl:
            self.parse__func_declaration_end()

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
    def parse__preprocessorif(self):
        """
                CppParser.parse__preprocessorif()
                ________________________________________________________________

                A member of the parse__* functions (see general indications
                above).

                Function called when the parser reads a line beginning with a
                if-preprocessor directive
        """
        if self.current_lliaf.lines.startswith(("#if", "#ifdef", "#ifndef")):
            self.state.preprocessorif.append(self.current_lliaf.lines)

        elif self.current_lliaf.lines.startswith(("#else", "#elif")):
            if len(self.state.preprocessorif) == 0:
                msg = "Can't take in account the #else/#elif directive : no #if/#ifdef/#ifndef " \
                      "preceding directive; " \
                      "details : " + repr(self.current_lliaf)
                MSG.error(msg)
            self.state.preprocessorif[-1] = self.current_lliaf.lines

        elif self.current_lliaf.lines.startswith("#endif"):
            self.state.preprocessorif.pop()

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
        line = self.current_lliaf.lines[2:]
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
        line = self.current_lliaf.lines[2:]
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
        if len(self.current_lliaf.lines):
            self.state.current_block_of_comments.append(self.current_lliaf.lines)

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
        self.root = ""
        self.current_lliaf = LLIAF()
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
