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
        ❏Eupompos❏ eupompos/parsertools.py

        o FunctionDeclaration class
"""

################################################################################
class FunctionDeclaration(object):
    """
        FunctionDeclaration class
        ________________________________________________________________________

        Use this class to read/write informations about a function/method name
        ________________________________________________________________________

        class attributes : -

        instance attributes :

            o module      : (None/str)
            o classname   : (None/str)
            o functioname : (str)
            o liaf        : LIAF object

        methods :

            o __init__()
            o __repr__()
            o get_uniquename()
            o init_from_str()
            o is_defined()
            o xrepr()
    """
    #///////////////////////////////////////////////////////////////////////////
    def __init__(self, _modulename=None, _classname=None, _functionname=None, _liaf=None):
        """
                FunctionDeclaration.__init__()
                ________________________________________________________________

                Create the attributes.
                ________________________________________________________________

                PARAMETERS :
                    o _modulename   : None/str
                    o _classname    : None/str
                    o _functionname : None/str
                    o _liaf         : LIAF object

                RETURNED VALUE : no RETURNED VALUE
        """
        self.modulename = _modulename
        self.classname = _classname
        self.functionname = _functionname
        self.liaf = _liaf

    #///////////////////////////////////////////////////////////////////////////
    def __lt__(self, _other):
        """
                FunctionDeclaration.__lt__()
                ________________________________________________________________

                Return True if self < _other; None is lower than a string.
                ________________________________________________________________

                PARAMETER :
                    o _other : another FunctionDeclaration object

                RETURNED VALUE : the expected boolean
        """
        # modules' name :
        if self.modulename is None and _other.modulename is not None:
            return True
        elif self.modulename is not None and _other.modulename is None:
            return False
        elif self.modulename != _other.modulename:
            return self.modulename < _other.modulename

        # classes' name :
        if self.classname is None and _other.classname is not None:
            return True
        elif self.classname is not None and _other.classname is None:
            return False
        elif self.classname != _other.classname:
            return self.classname < _other.classname

        # functions' name :
        return self.functionname < _other.functionname

    #///////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                FunctionDeclaration.__repr__()
                ________________________________________________________________

                Return a string representation of self.
                ________________________________________________________________

                no PARAMETER

                RETURNED VALUE : the expected string
        """
        return self.xrepr(_with_liaf=True)

    #///////////////////////////////////////////////////////////////////////////
    def get_uniquename(self):
        """
                FunctionDeclaration.get_uniquename()
                ________________________________________________________________

                Return a string representation of the name of self. This string
                has to be unique.
                ________________________________________________________________

                no PARAMETER

                RETURNED VALUE : the expected string
        """
        if self.modulename is None:
            if self.classname is not None:
                res = "{0}::{1}()".format(self.classname,
                                          self.functionname)
            else:
                res = "{0}()".format(self.functionname)

        else:
            if self.classname is not None:
                res = "{0}~{1}::{2}()".format(self.modulename,
                                              self.classname,
                                              self.functionname)
            else:
                res = "{0}~{1}()".format(self.modulename,
                                         self.functionname)

        return res

    #///////////////////////////////////////////////////////////////////////////
    def init_from_str(self, _str, _language):
        """
                FunctionDeclaration.__repr__()
                ________________________________________________________________

                Initialize self.classname and self.functionname from a string :
                the other attributes won't change.
                ________________________________________________________________

                PARAMETERS :
                    _str      : source string
                    _language : (str) "cpp" or "python"

                RETURNED VALUE : return self
        """
        if _language == "cpp":
            if "::" in _str:
                self.classname = _str[:_str.find("::")]
                self.functionname = _str[_str.find("::")+2:]
            else:
                self.classname = None
                self.functionname = _str

        return self

    #///////////////////////////////////////////////////////////////////////////
    def is_defined(self):
        """
                FunctionDeclaration.is_defined()
                ________________________________________________________________

                Return True if the function's name has been defined.
                ________________________________________________________________

                no PARAMETER

                RETURNED VALUE : the expected boolean
        """
        return self.functionname is not None

    #///////////////////////////////////////////////////////////////////////////
    def xrepr(self, _with_liaf=True, _prefix_before_line=""):
        """
                FunctionDeclaration.xrepr()
                ________________________________________________________________

                Return a string representation of self.
                ________________________________________________________________

                PARAMETERS :
                    o _with_liaf : (bool) True if the returned string ends
                                    with the informations stored in the
                                    LIAF object.
                    o _prefix_before_line : (str) the string to be added
                                            at the beginning of the returned string.

                RETURNED VALUE : the expected string
        """
        if not self.is_defined():
            return "(undefined)"

        res = self.get_uniquename()

        if _with_liaf:
            res += " in {0}".format(self.liaf.pos_and_lines_repr(_prefix_before_line))

        return res
