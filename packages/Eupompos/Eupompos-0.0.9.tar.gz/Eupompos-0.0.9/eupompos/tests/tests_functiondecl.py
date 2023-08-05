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

        Tests of the FunctionDeclaration class
        ________________________________________________________________________

        o TestsFunctionDeclaration class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error
import unittest

from   eupompos.parsertools import FunctionDeclaration

################################################################################
class TestsFunctionDeclaration(unittest.TestCase):
    """
        TestsFunctionDeclaration class
        ________________________________________________________________________

	Testing the FunctionDeclaration class
        ________________________________________________________________________

        class attributes : -

        instance attributes : -

        class methods :

            o test__functions()
    """

    #//////////////////////////////////////////////////////////////////////////
    def test__lt1(self):
        """
		TestsStrTools.test__lt1()
                ________________________________________________________________

		Test of objects' comparision (no module name)
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        funcdecl1 = FunctionDeclaration("class1", "func1")
        funcdecl2 = FunctionDeclaration("class2", "func2")
        self.assertTrue(funcdecl1 < funcdecl2)
        self.assertTrue(funcdecl2 > funcdecl1)
        self.assertTrue(funcdecl2 != funcdecl1)

        funcdecl1 = FunctionDeclaration("class1", "func1")
        funcdecl2 = FunctionDeclaration("class2", "func2")
        funcdecl3 = FunctionDeclaration("class3", "func3")
        self.assertTrue(funcdecl1 < funcdecl2 < funcdecl3)
        self.assertTrue(funcdecl3 > funcdecl2 > funcdecl1)

        funcdecl1 = FunctionDeclaration(None, "func1")
        funcdecl2 = FunctionDeclaration(None, "func2")
        self.assertTrue(funcdecl1 < funcdecl2)

        funcdecl1 = FunctionDeclaration(None, "func1")
        funcdecl2 = FunctionDeclaration("abc", "func2")
        self.assertTrue(funcdecl1 < funcdecl2)

        funcdecl1 = FunctionDeclaration(None, "func1")
        funcdecl2 = FunctionDeclaration("abc", "abc")
        self.assertTrue(funcdecl1 < funcdecl2)

        funcdecl1 = FunctionDeclaration(None, "func1")
        funcdecl2 = FunctionDeclaration("abc", "gh")
        self.assertTrue(funcdecl1 < funcdecl2)

        funcdecl1 = FunctionDeclaration("abc", "efg")
        funcdecl2 = FunctionDeclaration("abc", "hji")
        self.assertTrue(funcdecl1 < funcdecl2)

        funcdecl1 = FunctionDeclaration("abc", "efg")
        funcdecl2 = FunctionDeclaration(None, "hji")
        self.assertTrue(funcdecl1 > funcdecl2)

        funcdecl1 = FunctionDeclaration("TextFormat", "TextFormat")
        funcdecl2 = FunctionDeclaration("UI", "UI")
        funcdecl3 = FunctionDeclaration("MainWindow", "about")
        self.assertTrue(funcdecl3 < funcdecl1 < funcdecl2)

    #//////////////////////////////////////////////////////////////////////////
    def test__lt2(self):
        """
		TestsStrTools.test__lt2()
                ________________________________________________________________

		Test of objects' comparision
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        funcdecl1 = FunctionDeclaration("module1", "class1", "func1")
        funcdecl2 = FunctionDeclaration("module2", "class2", "func2")
        self.assertTrue(funcdecl1 < funcdecl2)
        self.assertTrue(funcdecl2 > funcdecl1)
        self.assertTrue(funcdecl2 != funcdecl1)

        funcdecl1 = FunctionDeclaration("module1", "class1", "func1")
        funcdecl2 = FunctionDeclaration("module2", "class2", "func2")
        self.assertTrue(funcdecl1 < funcdecl2)
        self.assertTrue(funcdecl2 > funcdecl1)
        self.assertTrue(funcdecl2 != funcdecl1)

        funcdecl1 = FunctionDeclaration(None, "class1", "func1")
        funcdecl2 = FunctionDeclaration("module2", "class2", "func2")
        self.assertTrue(funcdecl1 < funcdecl2)
        self.assertTrue(funcdecl2 > funcdecl1)
        self.assertTrue(funcdecl2 != funcdecl1)
