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
        ❏Eupompos❏ ./tests/tests_cppparser.py
        ________________________________________________________________________

        Tests of the cppparser.py script
        ________________________________________________________________________

        o TestsCppParser class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import unittest
import os.path

import eupompos.configfile as configfile
import eupompos.main
from   eupompos.parser import Parser
import eupompos.settings as settings

configfile.read_configfile(os.path.join("eupompos", "tests", "eupompos1.ini"))
eupompos.main.init_settings_from_cfgfile(settings, configfile)

################################################################################
class TestsCppParser(unittest.TestCase):
    """
        TestsCppParser class
        ________________________________________________________________________

	Testing the cppparser.py script
        ________________________________________________________________________

        class attributes : -

        instance attributes : -

        class methods :

            o test__functions1()
            o test__functions2()
    """

    #//////////////////////////////////////////////////////////////////////////
    def test__functions1(self):
        """
		TestsCppParser.test__functions1()
                ________________________________________________________________

		Test of the parsing of the functions : functions' name .
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        # let's read the source :
        dataparser = Parser(os.path.join("eupompos", "tests", "cppfiles002"))

        self.assertEqual(len(dataparser.report.functions), 4)

        key = "sctabs.cpp@SCTabs::tabInserted(int index)+void"
        self.assertTrue(key in dataparser.report.functions.keys())

        key = "sctabs.cpp@SCTabs::SCTabs(QWidget *_parent)"
        self.assertTrue(key in dataparser.report.functions.keys())
        self.assertEqual(dataparser.report.functions[key].comments,
                         ["SCTabs::SCTabs", "SCTabs' constructor."])
