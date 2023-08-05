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
        ❏Eupompos❏ eupompos/cppfuncdecl.py

        o FunctionDeclaration class
"""
import re

import eupompos.settings as settings

################################################################################
class FunctionDeclaration(object):
    """
        FunctionDeclaration class
        ________________________________________________________________________

        Use this class to read/write informations about a function/method name
        ________________________________________________________________________

        class attributes : -

        instance attributes :

            o preprocessorif : (str)
            o modulename  : (str)
            o classname   : (None/str)
            o functioname : (str)
            o functionarguments : (str)
            o returnedtype : (None/str)
            o completedecl: (str)
            o data        : LLIAF object

        methods :

            o __init__()
            o __repr__()
            o get_infos_about_funcdecl()
            o get_uniquename()
            o init_from_data()
            o is_defined()
            o xrepr()
    """
    #///////////////////////////////////////////////////////////////////////////
    def __init__(self,
                 _modulename="",
                 _classname=None,
                 _functionname="",
                 _functionarguments=None,
                 _returnedtype=None,
                 _data=None,
                 _completedecl=None):
        """
                FunctionDeclaration.__init__()
                ________________________________________________________________

                Create the attributes.
                ________________________________________________________________

                PARAMETERS :
                    o _modulename   : str
                    o _classname    : None/str
                    o _functionname : str
                    o _functionarguments : None/str
                    o _returnedtype : None/str
                    o _data        : LLIAF object

                RETURNED VALUE : no RETURNED VALUE
        """
        self.preprocessorif = []
        self.modulename = _modulename
        self.classname = _classname
        self.functionname = _functionname
        self.functionarguments = _functionarguments
        self.returnedtype = _returnedtype
        self.data = _data
        self.completedecl = _completedecl

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
        # module's name :
        if self.modulename != _other.modulename:
            return self.modulename < _other.modulename

        # preprocessor if :
        if self.preprocessorif != _other.preprocessorif:
            return self.preprocessorif < _other.preprocessorif

        # classes' name :
        if self.classname is None and _other.classname is not None:
            return True
        elif self.classname is not None and _other.classname is None:
            return False
        elif self.classname != _other.classname:
            return self.classname < _other.classname

        # functions' name :
        if self.functionname != _other.functionname:
            return self.functionname < _other.functionname

        # returned type :
        if self.returnedtype != _other.returnedtype:
            return self.returnedtype < _other.returnedtype

        # arguments :
        return self.functionarguments < _other.functionarguments

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
        return self.xrepr(_with_data=True)

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def get_infos_about_funcdecl(_lines):
        """
                FunctionDeclaration.get_infos_about_funcdecl()
                ________________________________________________________________

                Analyse (str)_lines : return the returned type, the function
                name, the function's class and the arguments . E.g. :
                        void Class::foo(int i) -> ("void", "Class", "foo", "int i")
                ________________________________________________________________

                PARAMETER :
                    o _lines    : (str) the function declaration,

                RETURNED VALUE : ( (str/None)function' arguments,
                                   (str/None)returned type,
                                   (str/None)class name,
                                   (str)function name )
        """
        # the regex returns (returnedtype,
        #                    classname,
        #                    functionname,
        #                    initializer)
        returnedtype, classname, functionname, functionarguments, _ = \
                                re.search(settings.REGEX__CPP_FUNCTIONDECLARATION,
                                          _lines).groups()

        if functionarguments is not None:
            functionarguments = functionarguments.strip()

        if classname is not None:
            classname = classname.replace("::", "").strip()

        if returnedtype is not None:
            returnedtype = returnedtype.strip()

        return functionarguments, returnedtype, classname, functionname

    #///////////////////////////////////////////////////////////////////////////
    def get_uniquename(self, _returnedtype_at_the_end=True):
        """
                FunctionDeclaration.get_uniquename()
                ________________________________________________________________

                Return a string representation of the name of self. This string
                has to be unique.
                ________________________________________________________________

                PARAMETER :
                    o _returnedtype_at_the_end : (bool) if set to True,
                      add the returned type at the end of the returned string,
                      not at the beginning.
                        void foo(int)   -> foo(int)+void
                        int foo(int)    -> foo(int)+int

                      Such a string is convenient to sort functions's names.

                RETURNED VALUE : the expected string
        """
        # arguments, class name, function name and complete declaration :
        functionarguments = ""
        if self.functionarguments is not None:
            functionarguments = self.functionarguments

        preprocessorif = ""
        if len(self.preprocessorif) > 0:
            preprocessorif = "{{{"+self.preprocessorif+"}}}"

        classname = ""
        if self.classname is not None:
            classname = self.classname + "::"

        res = "{0}@{1}{2}({3}){4}".format(self.modulename,
                                          classname,
                                          self.functionname,
                                          functionarguments,
                                          preprocessorif)

        # returned type :
        if self.returnedtype is not None:
            if not _returnedtype_at_the_end:
                res = self.returnedtype + " " + res
            else:
                res = res + "+" + self.returnedtype

        # returned value :
        return res

    #///////////////////////////////////////////////////////////////////////////
    def init_from_data(self, preprocessorif):
        """
                FunctionDeclaration.init_from_data()
                ________________________________________________________________

                Initialize self.completedecl, self.classname, self.functionname
                and self.returnedtype from self.data .
                ________________________________________________________________

                PARAMETER :
                    o preprocessorif : a list of str.

                no RETURNED VALUE
        """
        self.preprocessorif = "/#/".join(preprocessorif)
        self.modulename = self.data.filename

        completedecl = []
        stop = False
        for line in self.data.lines:
            _line = line

            if "{" in _line:
                _line = _line[:_line.find("{")]
                stop = True

            if " : " in line:
                _line = _line[:_line.find(" : ")]
                stop = True

            _line = _line.strip()
            completedecl.append(_line)

            if stop:
                break

        self.completedecl = " ".join(completedecl).strip()
        self.functionarguments, self.returnedtype, self.classname, self.functionname = \
                        self.get_infos_about_funcdecl(_lines=self.completedecl)

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
        return self.functionname is not ""

    #///////////////////////////////////////////////////////////////////////////
    def xrepr(self, _with_data=True, _prefix_before_line=""):
        """
                FunctionDeclaration.xrepr()
                ________________________________________________________________

                Return a string representation of self.
                ________________________________________________________________

                PARAMETERS :
                    o _with_data : (bool) True if the returned string ends
                                    with the informations stored in the
                                    LLIAF object.
                    o _prefix_before_line : (str) the string to be added
                                            at the beginning of the returned string.

                RETURNED VALUE : the expected string
        """
        if not self.is_defined():
            return "(undefined)"

        functionarguments = ""
        if self.functionarguments is not None:
            functionarguments = self.functionarguments

        returnedtype = ""
        if self.returnedtype is not None:
            returnedtype = self.returnedtype

        preprocessorif = ""
        if len(self.preprocessorif) > 0:
            preprocessorif = "{{{"+self.preprocessorif+"}}}"

        classname = ""
        if self.classname is not None:
            classname = self.classname + "::"

        res = "{0} {1}::{2}({3}) {4}".format(returnedtype,
                                             classname,
                                             self.functionname,
                                             functionarguments,
                                             preprocessorif)

        if _with_data:
            res += " in {0}".format(self.data.pos_and_lines_repr(_prefix_before_line))

        return res
