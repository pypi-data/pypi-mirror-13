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
        ❏Eupompos❏ ./tests/tests_pyparser.py
        ________________________________________________________________________

        Tests of the pyparser.py script
        ________________________________________________________________________

        o TestsPyParser class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error
import unittest
import os.path

from   eupompos.parser import Parser
import eupompos.configfile as configfile
import eupompos.settings as settings
import eupompos.main

configfile.read_configfile(os.path.join("eupompos", "tests", "eupompos1.ini"))
eupompos.main.init_settings_from_cfgfile(settings, configfile)

################################################################################
class TestsPyParser(unittest.TestCase):
    """
        TestsPyParser class
        ________________________________________________________________________

	Testing the pypparser.py script
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
		TestsStrTools.test__functions1()
                ________________________________________________________________

		Test of the parsing of the functions : functions' name .
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        # let's read the source :
        data = Parser(os.path.join("eupompos", "tests", "pyfiles001"))
        self.assertEqual(len(data.report.functions), 4)

        func = "qtapplication.py~SplashScreen::__init__()"
        self.assertTrue(func in data.report.functions)

        func = "qtapplication.py~create_and_launch_the_Qt_application()"
        self.assertTrue(func in data.report.functions)

    #//////////////////////////////////////////////////////////////////////////
    def test__functions2(self):
        """
		TestsStrTools.test__functions2()
                ________________________________________________________________

		Test of the parsing of the functions : functions' comments
                ________________________________________________________________

                no PARAMETER, no RETURNED VALUE
        """
        # let's read the source :
        data = Parser(os.path.join("eupompos", "tests", "pyfiles001"))

        func_name = "qtapplication.py~SplashScreen::__init__()"
        self.assertEqual(len(data.report.functions[func_name].comments), 1)
        self.assertEqual(data.report.functions[func_name].comments,
                         [" "*16+"SplashScreen.__init__",])
