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
        ❏Eupompos❏ eupompos/pyparserstate.py

        o DocstringsBlock class
        o PyParserState class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import copy

from eupompos.pyfuncdecl import FunctionDeclaration

################################################################################
class DocstringsBlock(object):
    """
        DocstringsBlock class .
        ________________________________________________________________________

        Class used by by PyParserState.current_block_of_docstrings .
        ________________________________________________________________________

        class attributes : -

        instance attributes :

            o liaf : a LIAF object
            o lines : a list of strings.

        methods :

            o __init__()
            o __copy__()
            o clear()
            o xrepr()
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, _liaf=None, _lines=None):
        """
                DocstringsBlock.__init__()
                ________________________________________________________________

                Create the attributes.
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : no RETURNED VALUE
        """
        self.liaf = _liaf      # a LIAF object

        if _lines is None:
            self.lines = []
        else:
            self.lines = _lines     # a list of strings

    #///////////////////////////////////////////////////////////////////////////
    def __copy__(self):
        """
                DocstringsBlock.__copy__()
                ________________________________________________________________

                Deep copy of the object
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : a DocstringsBlock object.
        """
        return DocstringsBlock(_liaf=copy.copy(self.liaf),
                               _lines=copy.copy(self.lines))

    #///////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                DocstringsBlock.__repr__()
                ________________________________________________________________

                Return a full description of the object
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : the expected string
        """
        return self.xrepr()

    #///////////////////////////////////////////////////////////////////////////
    def clear(self):
        """
                DocstringsBlock.clear()
                ________________________________________________________________

                Set the attributes to their default value.
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : no RETURNED VALUE
        """
        self.liaf = None
        self.lines = []

    #///////////////////////////////////////////////////////////////////////////
    def xrepr(self):
        """
                DocstringsBlock.xrepr()
                ________________________________________________________________

                Return a full description of the object
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : the expected string
        """
        return "liaf={0}; lines={1}".format(self.liaf.pos_repr(),
                                            self.lines)

################################################################################
class PyParserState(object):
    """
        PyParserState class
        ________________________________________________________________________

        Class used by a PyParser object to store temporary informations about
        the current file.
        ________________________________________________________________________

        class attributes : -

        instance attributes :

            o current_block_of_docstrings : a DocstringsBlock object
            o current_class : str
            o current_connections_line : list of strings
            o current_funcdecl : FunctionDeclaration (never None)
            o inside_docstring : boolean

        methods :

            o __init__()
            o __repr__()
            o reset()
            o xrepr()
    """

    #//////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
                PyParserState.__init__()
                ________________________________________________________________

                Create the attributes, set them to None and call .reset() to
                initialize these attributes to a default value.
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : no RETURNED VALUE
        """
        self.current_block_of_docstrings = None
        self.current_class = None
        self.current_connections_line = None
        self.current_funcdecl = FunctionDeclaration()
        self.inside_docstring = False

        self.reset()

    #//////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                PyParserState.__repr__()
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
                PyParserState.reset()
                ________________________________________________________________

                Set the attributes to their default value.
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : no RETURNED VALUE
        """
        self.current_block_of_docstrings = DocstringsBlock()
        self.current_class = None
        self.current_connections_line = []
        self.current_funcdecl = FunctionDeclaration()
        self.inside_docstring = False

    #//////////////////////////////////////////////////////////////////////////
    def xrepr(self):
        """
                PyParserState.xrepr()
                ________________________________________________________________

                Return a string describing self.
                ________________________________________________________________

                PARAMETER(S) : no parameter

                RETURNED VALUE : no RETURNED VALUE
        """
        return "(PyParserState) class={0}; " \
               "connections line={1}; " \
               "function={2}; " \
               "docstring={3}/inside docstring={4}".format(self.current_class,
                                                           self.current_connections_line,
                                                           self.current_funcdecl,
                                                           self.current_block_of_docstrings,
                                                           self.inside_docstring)
