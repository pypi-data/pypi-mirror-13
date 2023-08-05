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
        ❏Eupompos❏ eupompos/parserreport.py
        ________________________________________________________________________

        report object used by the Parse classes.
        ________________________________________________________________________

        o ParserReportFunction type
        o ParserReport class
"""

# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

from   eupompos.strtools import add_prefix_to_lines, rm_initial_spaces
import eupompos.settings as settings

################################################################################
class ParserReportFunction(object):
    """
        ParserReportFunction class
        ________________________________________________________________________

        Class used in ParserReport.functions dict
        ________________________________________________________________________

        class attributes : -

        instance attribute(s) : -

            o function : a FunctionDeclaration object
            o comments : a list of strings

        class methods :

            o __init__()
            o __repr__()
            o init()
            o xrepr()
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
                ParserReportFunction.__init__()
                ________________________________________________________________

                Define the instance attributes.
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        self.function = None    # FunctionDeclaration object
        self.comments = []      # a list of strings

    #///////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                ParserReportFunction.__repr__()
                ________________________________________________________________

                Return a string representation of the object.
                ________________________________________________________________

                no PARAMETER

                RETURNED VALUE : the expected string
        """
        return self.xrepr(_prefix_before_commentline="",
                          _comments_on_several_lines=False)

    #///////////////////////////////////////////////////////////////////////////
    def init(self, _function, _comments_lines, _usefull_line):
        """
                ParserReportFunction.__init__()
                ________________________________________________________________

                Initialize self from a function described by the FunctionDeclaration
                object _function and from a list of lines.
                ________________________________________________________________

                PARAMETERS :
                    o _function         : a FunctionDeclaration object
                    o _comments_lines   : a list of strings
                    o _usefull_line     : a function returning True[/False] if
                                          a line is[/n't] usefull

                RETURNED VALUE : self
        """
        self.comments.clear()

        self.function = _function

        for line in _comments_lines:
            if _usefull_line(line):
                self.comments.append(line)

        return self

    #///////////////////////////////////////////////////////////////////////////
    def xrepr(self, _prefix_before_commentline, _comments_on_several_lines):
        """
                ParserReportFunction.xrepr()
                ________________________________________________________________

                Return a string representation of the object
                ________________________________________________________________

                PARAMETER :
                    o _comments_on_several_lines : (bool) if True, the comments
                                                   will appear on several lines.
                    o _prefix_before_commentline  : (str) prefix added at the
                                                    beginning of each comment's
                                                    line

                RETURNED VALUE : the expected string
        """
        if not _comments_on_several_lines:
            return "{0}, comments={1}".format(self.function, self.comments)
        else:
            res = "{0}".format(self.function.xrepr(_with_liaf=True,
                                                   _prefix_before_line=\
                                                        "\n   - function declaration :"))
            res += "\n   - function's comments :"
            for line in self.comments:
                res += "\n{0}{1}".format(_prefix_before_commentline, line)
            return res

################################################################################
class ParserReport(object):
    """
        ParserReport class
        ________________________________________________________________________

        Object filled by the Parser methods.
        ________________________________________________________________________

        class attributes : -

        instance attribute(s) : -

            o functions : (dict) (str)full name -> ParserReportFunction object
            o errors : a list of strings

        class methods :

            o __init__()
            o __repr__()
            o clear()
            o xrepr()
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
                ParserReport.__init__()
                ________________________________________________________________

                Define the instance attributes.
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        self.functions = dict()
        self.errors = list()

    #///////////////////////////////////////////////////////////////////////////
    def __repr__(self):
        """
                ParserReport.__repr__()
                ________________________________________________________________

                Straightforward representation of the report.
                ________________________________________________________________

                no PARAMETER

                RETURNED VALUE : the expected string
        """
        return self.xrepr(settings.PARSERREPORT__FUNCPOS_MAXLENGTH)

    #///////////////////////////////////////////////////////////////////////////
    def add_function(self, _funcdecl, _comments_lines, _usefullcommentline_func):
        """
                ParserReport.add_function()
                ________________________________________________________________

                Add a function to self.functions
                ________________________________________________________________

                PARAMETERS :
                    o _funcdecl                 : a FunctionDeclaration object
                    o _comments_lines           : a list of strings
                    o _usefullcommentline_func  : a function checking if a line
                                                  may be a usefull comment line.
                no RETURNED VALUE
        """
        # the key corresponding to _funcdecl as stored in self.functions :
        key = _funcdecl.get_uniquename()

        if key in self.functions:

            # prefix before line : (first/second function)
            pbl_1 = "\n   - function declaration : "
            pbl_2 = "        « "

            errmsg = "The following function definition is ambiguous;" \
                     " another function already bears the same name : " \
                     "\n* first function = {0}; " \
                     "\n* second function = {1}".format(self.functions[key].xrepr(pbl_1, True),
                                                        _funcdecl.xrepr(_with_liaf=True,
                                                                        _prefix_before_line=pbl_2))
            self.errors.append(errmsg)

        else:
            self.functions[key] = \
                ParserReportFunction().init(_funcdecl,
                                            _comments_lines,
                                            _usefullcommentline_func)

    #///////////////////////////////////////////////////////////////////////////
    def clear(self):
        """
                ParserReport.clear()
                ________________________________________________________________

                Reset the values of self.
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        self.functions.clear()

    #///////////////////////////////////////////////////////////////////////////
    def xrepr(self, _funcpos_max_length):
        """
                ParserReport.xrepr()
                ________________________________________________________________

                Straightforward representation of the report.
                ________________________________________________________________

                PARAMETER :
                    o _funcpos_max_length : (int) maximal length of the string
                                            describing the function position
                                            in a file.

                RETURNED VALUE : the expected string
        """
        res = ["report :",]

        if len(self.errors) == 0:
            res.append("No error occured.")
            res.append("")
        elif len(self.errors) == 1:
            res.append("! One error occured :")
            res.append(self.errors[0])
            res.append("")
        else:
            res.append("! {0} errors occured.".format(len(self.errors)))
            for error_index, error_msg in enumerate(self.errors):
                res.append("o  error #{0} :".format(error_index))
                for line in add_prefix_to_lines(error_msg.split("\n"), " "*3):
                    res.append(line)
                res.append("")

        if len(self.functions) == 0:
            res.append("function(s) : no function !")

        else:
            if len(self.functions) == 1:
                res.append("functions : (read 1 function)")
            else:
                res.append("functions : (read {0} functions)".format(len(self.functions)))

            for func_name in sorted(self.functions):

                function = self.functions[func_name].function
                comments = self.functions[func_name].comments

                res.append("")
                res.append("o  {0}".format(function.xrepr(_with_liaf=False)))
                res.append("   defined in {0}.".format(function.liaf.pos_repr(_funcpos_max_length)))

                if len(comments) > 0:
                    comm = add_prefix_to_lines(rm_initial_spaces(comments),
                                               "       « ")
                    res.append("   \n{0}".format("\n".join(comm)))

        return "\n".join(res)
