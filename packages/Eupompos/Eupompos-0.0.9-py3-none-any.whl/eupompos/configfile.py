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
        ❏Eupompos❏ eupompos/configfile.py
        ________________________________________________________________________

        tools to access the content of the configuration file of the project.
        ________________________________________________________________________

        o CONFIGDATA
        o read_configfile()
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import configparser
import os.path

from eupompos.messages import MSG
from eupompos.strtools import add_prefix_to_lines

# initialized by read_configfile()
CONFIGDATA = configparser.ConfigParser()

#///////////////////////////////////////////////////////////////////////////////
def read_configfile(_configfile_name):
    """
        read_configfile()
        ________________________________________________________________________

        fill CONFIGDATA from a configuration file.
        ________________________________________________________________________

        PARAMETER :
            o (str)_configfile_name

        RETURNED VALUE : (bool) success; has the configuration file been
                       correctly read ?
    """
    res = True

    if not os.path.exists(_configfile_name):
        MSG.error("! the expected config file \"{0}\" doesn't exist.".format(_configfile_name))
        res = False

    try:
        CONFIGDATA.read(_configfile_name)

    except configparser.Error as exception:
        MSG.error("! ill-formed config file \"{0}\"".format(_configfile_name))
        MSG.error("! error message : \n"+add_prefix_to_lines(str(exception), "    : "))

        res = False

    return res
