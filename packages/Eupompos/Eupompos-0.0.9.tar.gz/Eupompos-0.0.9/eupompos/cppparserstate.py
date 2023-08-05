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
        ❏Eupompos❏ eupompos/cppparserstate.py

        o CppParserState class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

from eupompos.parsertools import FunctionDeclaration

################################################################################
class CppParserState(object):
    """
        CppParserState class
        ________________________________________________________________________

        Class used by a CppParser object to store temporary informations about
        the current file.
        ________________________________________________________________________

        class attributes : -

        instance attributes :

            o current_block_of_comments : list of strings
            o current_function : FunctionDeclaration
            o inside_slashstar : (None if non initialized) bool
            o current_connections_line : list of strings

        methods :

            o __init__()
            o __repr__()
            o reset()
            o xrepr()
    """

    #//////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
                CppParserState.__init__()
                ________________________________________________________________

                Create the attributes, set them to None and call .reset() to
                initialize these attributes to a default value.
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : no RETURNED VALUE
        """
        self.inside_slashstar = None
        self.current_function = None
        self.current_connections_line = None
        self.current_block_of_comments = None

        self.reset()

    #//////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                CppParserState.__repr__()
                ________________________________________________________________

                Return a string describing self.
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : no RETURNED VALUE
        """
        return self.xrepr()

    #//////////////////////////////////////////////////////////////////////////
    def reset(self):
        """
                CppParserState.reset()
                ________________________________________________________________

                Set the attributes to their default value.
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : no RETURNED VALUE
        """
        self.inside_slashstar = False
        self.current_function = FunctionDeclaration()
        self.current_connections_line = []
        self.current_block_of_comments = []

    #//////////////////////////////////////////////////////////////////////////
    def xrepr(self):
        """
                CppParserState.xrepr()
                ________________________________________________________________

                Return a string describing self.
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : no RETURNED VALUE
        """
        return "(CppParserState) inside slash star={0}; " \
               "connections line={1}; " \
               "function={2}; comments={3}".format(self.inside_slashstar,
                                                   self.current_connections_line,
                                                   self.current_function,
                                                   self.current_block_of_comments)



























