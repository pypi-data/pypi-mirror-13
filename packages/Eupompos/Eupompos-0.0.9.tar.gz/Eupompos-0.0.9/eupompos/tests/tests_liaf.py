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
        ❏Eupompos❏ ./tests/tests_liaf.py
        ________________________________________________________________________

        Tests of the liaf.py module.
        ________________________________________________________________________

        o TestsLIAF class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import copy
import unittest

from eupompos.liaf import LIAF

################################################################################
class TestsLIAF(unittest.TestCase):
    """
        TestsLIAF class
        ________________________________________________________________________

	Testing the liaf module
        ________________________________________________________________________

        class attributes : -

        instance attributes : -

        class methods :

            o test__copy()
    """

    #//////////////////////////////////////////////////////////////////////////
    def test__copy(self):
        """
		TestsLIAF.test__copy
                ________________________________________________________________

		Test of liaf.LIAF.__copy__() .
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        liaf1 = LIAF(_filename="xx.py",
                     _linenumber=3,
                     _line="yyy")

        liaf2 = copy.copy(liaf1)

        self.assertEqual(liaf1, liaf1)
        self.assertEqual(liaf1, liaf2)

        liaf3 = copy.copy(liaf1)
        liaf3.filename = "yy.py"
        self.assertNotEqual(liaf1, liaf3)
        self.assertEqual(liaf1.filename, "xx.py")
        self.assertEqual(liaf3.filename, "yy.py")

        liaf4 = copy.copy(liaf1)
        liaf4.linenumber = 99
        self.assertNotEqual(liaf1, liaf4)
        self.assertEqual(liaf1.linenumber, 3)
        self.assertEqual(liaf4.linenumber, 99)

        liaf5 = copy.copy(liaf1)
        liaf5.line = "zzz"
        self.assertNotEqual(liaf1, liaf5)
        self.assertEqual(liaf1.line, "yyy")
        self.assertEqual(liaf5.line, "zzz")
