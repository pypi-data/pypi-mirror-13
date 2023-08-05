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
        ❏Eupompos❏ eupompos/cppparser/liaf.py
        ________________________________________________________________________

        Tools usefull to read/write informations about a line in a file.
        LIAF is a language agnostic class.
        ________________________________________________________________________

        o LIAF class
"""

################################################################################
class LIAF(object):
    """
        L[ine] I[n] A F[ile]
        ________________________________________________________________________

        Simple class to store a filename, the line number and the line itself.
        ________________________________________________________________________

        class attribute :

            o LIAF.max_length_for_filename : (int) see pos_*() functions.

        instance attributes :

            o filename     : str or None if undefined
            o linenumber   : int or None if undefined
            o line         : str or None if undefined

        class methods :

            o __init__()
            o __copy__()
            o __eq__()
            o _repr__()
            o pos_and_line_repr()
            o pos_repr()
            o shorten()             [static]
    """

    # constant used by LIAF.shorten()
    max_length_for_filename = 100

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self,
                 _filename=None,
                 _linenumber=None,
                 _line=None):
        """
                LIAF.__init__()
                ________________________________________________________________

                PARAMETERS :

                o _filename     : (str, None if undefined)
                o _linenumber   : (int, None if undefined)
                o _line         : (str, None if undefined)

                RETURNED VALUE    : no RETURNED VALUE
        """
        self.filename = _filename
        self.linenumber = _linenumber
        self.line = _line

    #///////////////////////////////////////////////////////////////////////////
    def __copy__(self):
        """
                LIAF.__copy__()
                ________________________________________________________________

                return a copy of self
                ________________________________________________________________

                PARAMETER(S)    : no parameter

                RETURNED VALUE    : a LIAF object
        """
        return LIAF(_filename=self.filename,
                    _linenumber=self.linenumber,
                    _line=self.line)

    #///////////////////////////////////////////////////////////////////////////
    def __eq__(self, _other):
        """
                LIAF.__eq__()
                ________________________________________________________________

                return true if self and _other are equal.
                ________________________________________________________________

                PARAMETER(S)    : _other, a LIAF object

                RETURNED VALUE    : the expected boolean
        """
        return (self.filename == _other.filename) and \
               (self.linenumber == _other.linenumber) and \
               (self.line == _other.line)

    #///////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                LIAF.__repr__()
                ________________________________________________________________

                Return the state of the object in human readable way.
                All the informations appear in the returned string.
                ________________________________________________________________

                PARAMETER(S)    : no parameter

                RETURNED VALUE    : a string
        """
        return self.pos_and_lines_repr()

    #///////////////////////////////////////////////////////////////////////////
    def pos_and_lines_repr(self,
                           _prefix_before_line="\n   ",
                           _max_length_for_filename=max_length_for_filename):
        """
                LIAF.pos_and_lines_repr()
                ________________________________________________________________

                Return the state of the object in human readable way.
                All the informations appear in the returned string.
                ________________________________________________________________

                PARAMETERS :
                    o _prefix_before_line         : (str) string displayed before the line

                    o _max_length_for_filename    : (int) maximal length of the string
                                                          displaying the filename

                RETURNED VALUE    : a string
        """
        return "{0}#{1}{2}\"{3}\"".format(LIAF.shorten(self.filename, _max_length_for_filename),
                                          self.linenumber,
                                          _prefix_before_line,
                                          self.line)

    #///////////////////////////////////////////////////////////////////////////
    def pos_repr(self, _max_length_for_filename=max_length_for_filename):
        """
                LIAF.pos_repr()
                ________________________________________________________________

                Return the state of the object in human readable way.

                The line's content is not displayed.
                ________________________________________________________________

                PARAMETER(S)    : no parameter

                RETURNED VALUE    : a string
        """
        return "{0}#{1}".format(LIAF.shorten(self.filename, _max_length_for_filename),
                                self.linenumber)

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def shorten(_string, _max_length_for_filename):
        """
                LIAF.shorten()
                ________________________________________________________________

                Return a shortened version of "string", up to
                _max_length_for_filename characters.
                ________________________________________________________________

                PARAMETER :
                o _string       : (str) the source string

                RETURNED VALUE    : a string
        """
        if len(_string) > _max_length_for_filename:
            return "(...)" + _string[len(_string) - _max_length_for_filename:]
        else:
            return _string
