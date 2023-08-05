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
        ❏Eupompos❏ ./tests/tests_strtools.py
        ________________________________________________________________________

        Tests of the strtools.py script.
        ________________________________________________________________________

        o TestsStrTools class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import unittest
from eupompos.strtools import add_prefix_to_lines

################################################################################
class TestsStrTools(unittest.TestCase):
    """
        Tests class
        ________________________________________________________________________

	Testing the strtools.py script
        ________________________________________________________________________

        class attributes : -

        instance attributes : -

        class methods :

            o test__add_prefix1()
            o test__add_prefix2()
    """

    #//////////////////////////////////////////////////////////////////////////
    def test__add_prefix1(self):
        """
		TestsStrTools.test__add_prefix1()
                ________________________________________________________________

		Test of the strtools.py::add_prefix_to_lines()
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        lines = "123\n456"

        self.assertEqual(add_prefix_to_lines(lines, "..."),
                         "...123\n...456")

    #//////////////////////////////////////////////////////////////////////////
    def test__add_prefix2(self):
        """
		TestsStrTools.test__add_prefix2()
                ________________________________________________________________

		Test of the strtools.py::add_prefix_to_lines()
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        lines = ["123", "456"]

        self.assertEqual(add_prefix_to_lines(lines, "..."),
                         "...123\n...456")
