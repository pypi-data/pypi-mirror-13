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
        ❏Eupompos❏ ./tests/tests_functionname.py
        ________________________________________________________________________

        Tests of the FunctionName class
        ________________________________________________________________________

        o TestsFunctionName class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error
from   eupompos.parsertools import FunctionName

import unittest

################################################################################
class TestsFunctionName(unittest.TestCase):
    """
        TestsFunctionName class
        ________________________________________________________________________

	Testing the FunctionName class
        ________________________________________________________________________

        class attributes : -

        instance attributes : -

        class methods :

            o test__functions()
    """

    #//////////////////////////////////////////////////////////////////////////
    def test__lt(self):
        """
		TestsStrTools.test__kt()
                ________________________________________________________________

		Test of objects' comparision.
                ________________________________________________________________

                no PARAMETER, no RETURN VALUE
        """
        funcname1 = FunctionName("class1", "func1")
        funcname2 = FunctionName("class2", "func2")
        self.assertTrue(funcname1 < funcname2)
        self.assertTrue(funcname2 > funcname1)
        self.assertTrue(funcname2 != funcname1)

        funcname1 = FunctionName("class1", "func1")
        funcname2 = FunctionName("class2", "func2")
        funcname3 = FunctionName("class3", "func3")
        self.assertTrue(funcname1 < funcname2 < funcname3)
        self.assertTrue(funcname3 > funcname2 > funcname1)

        funcname1 = FunctionName(None, "func1")
        funcname2 = FunctionName(None, "func2")
        self.assertTrue(funcname1 < funcname2)

        funcname1 = FunctionName(None, "func1")
        funcname2 = FunctionName("abc", "func2")
        self.assertTrue(funcname1 < funcname2)

        funcname1 = FunctionName(None, "func1")
        funcname2 = FunctionName("abc", "abc")
        self.assertTrue(funcname1 < funcname2)

        funcname1 = FunctionName(None, "func1")
        funcname2 = FunctionName("abc", "gh")
        self.assertTrue(funcname1 < funcname2)

        funcname1 = FunctionName("abc", "efg")
        funcname2 = FunctionName("abc", "hji")
        self.assertTrue(funcname1 < funcname2)

        funcname1 = FunctionName("abc", "efg")
        funcname2 = FunctionName(None, "hji")
        self.assertTrue(funcname1 > funcname2)

        funcname1 = FunctionName("TextFormat", "TextFormat")
        funcname2 = FunctionName("UI", "UI")
        funcname3 = FunctionName("MainWindow", "about")
        self.assertTrue(funcname3 < funcname1 < funcname2)





