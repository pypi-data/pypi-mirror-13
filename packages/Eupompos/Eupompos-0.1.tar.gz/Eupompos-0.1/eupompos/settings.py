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
        ❏Eupompos❏ eupompos/settings.py
        ________________________________________________________________________

        Project's settings : global constants and variables.
        ________________________________________________________________________

        o PROJECT_NAME
        o PROJECT_VERSION
        o VERBOSITY
        o SOURCEPATH
        o CONFIGFILENAME

        o REGEX__PYTHON_FILENAMES
        o REGEX__PYTHON_CLASSDECLARATION
        o REGEX__PYTHON_FUNCTIONDECLARATION
        o REGEX__PYTHON_USEFULLCOM
        o REGEX__PYTHON_SHARPCOMMENT
        o REGEX__PYTHON_DOCSTRING
        o REGEX__PYTHON_DOCSTRING_UL
        o REGEX__CPP_CODE_FILENAMES
        o REGEX__CPP_FUNCTIONDECLARATIONSTART
        o REGEX__CPP_FUNCTIONDECLARATION
        o REGEX__CPP_USEFULLCOM
        o FULLNAME_BLACKLIST
        o PARSERREPORT__FUNCPOS_MAXLENGTH

        o __projectname__
        o __author__
        o __copyright__
        o __license__
        o __licensepipy__
        o __version__
        o __maintainer__
        o __email__
        o __status__
        o __statuspypi__
"""
PROJECT_NAME = "Eupompos"
# see https://www.python.org/dev/peps/pep-0440/
# e.g. 0.1.2.dev1, 0.0.6a0
PROJECT_VERSION = "0.1"

# see [doc:verbosity]
VERBOSITY = 3

# default source path where the cpp files are stored :
SOURCEPATH = "."

# default name of the configuration file :
# this variable may be modified by a command line parameter. See the --configfile option.
CONFIGFILENAME = "eupompos.ini"

# to be initialized by init_settings_from_cfgfile()
# these constants help the program to parse the files to be analysed :
REGEX__PYTHON_FILENAMES = None
REGEX__PYTHON_CLASSDECLARATION = None
REGEX__PYTHON_FUNCTIONDECLARATION = None
REGEX__PYTHON_USEFULLCOM = None
REGEX__PYTHON_SHARPCOMMENT = None
REGEX__PYTHON_DOCSTRING = None
REGEX__PYTHON_DOCSTRING_UL = None

REGEX__CPP_CODE_FILENAMES = None
REGEX__CPP_FUNCTIONDECLARATIONFIRSTLINE = None
REGEX__CPP_FUNCTIONDECLARATION = None
REGEX__CPP_USEFULLCOM = None

# is set to [] (not None) to avoid Pylint's complaints.
# -> FULLNAME_BLACKLIST will be initialized as a list !
FULLNAME_BLACKLIST = []

PARSERREPORT__FUNCPOS_MAXLENGTH = 100

# constants required by Pypi.
__projectname__ = PROJECT_NAME
__author__ = "Xavier Faure (suizokukan)"
__copyright__ = "Copyright 2015, suizokukan"
__license__ = "GPL-3.0"
# see https://pypi.python.org/pypi?%3Aaction=list_classifiers
__licensepipy__ = 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
# see https://www.python.org/dev/peps/pep-0440/
__version__ = PROJECT_VERSION
__maintainer__ = "Xavier Faure (suizokukan)"
__email__ = "suizokukan @T orange D@T fr"
__status__ = "Alpha"
# see https://pypi.python.org/pypi?%3Aaction=list_classifiers
__statuspypi__ = 'Development Status :: 3 - Alpha'
