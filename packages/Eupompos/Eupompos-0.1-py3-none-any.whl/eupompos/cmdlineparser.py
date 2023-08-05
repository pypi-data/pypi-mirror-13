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
        ❏Eupompos❏ eupompos/commandlineparser.py
        ________________________________________________________________________

        Project's command line parser.
        ________________________________________________________________________

        o CommandLineParser class
        o ARGS, unique instance of the CommandLineParser class
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import argparse

from eupompos.settings import PROJECT_NAME, PROJECT_VERSION, CONFIGFILENAME, \
                              __projectname__, __version__

################################################################################
class CommandLineParser(argparse.ArgumentParser):
    """
        CommandLineParser class
        ________________________________________________________________________

        Use this class to parse the command line arguments.

        Unique instance : ARGS (see at the end of the file)
        ________________________________________________________________________

        class attributes :

            o (str)description
            o (str)epilog

        instance attribute(s) : -

        class methods :

            o __init__()
            o explain_the_output()          [static]
            o get_args()
        ________________________________________________________________________
    """
    description = "{0} project, v.{1}".format(PROJECT_NAME,
                                              PROJECT_VERSION)

    epilog = "{0}'s author : " \
             "suizokukan (suizokukan _A.T_ orange DOT fr)".format(PROJECT_NAME)

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
                CommandLineParser.__init__()
                ________________________________________________________________

                Initialize the object by adding all the arguments.
                ________________________________________________________________

                PARAMETERS      : no parameter

                RETURNED VALUE    : no RETURNED VALUE
        """
        argparse.ArgumentParser.__init__(self,
                                         description=CommandLineParser.description,
                                         epilog=CommandLineParser.epilog,
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        self.add_argument('--sourcepath',
                          type=str,
                          help="source path of the C++ code")

        self.add_argument("--configfile",
                          type=str,
                          default=CONFIGFILENAME,
                          help="confile file name, by default ./eupompos.ini")

        self.add_argument("--download-configfile",
                          action="store_true",
                          help="download the default config file")

        self.add_argument('--verbosity',
                          type=int,
                          choices=(1, 2, 3, 4),
                          default=3,
                          help="degree of verbosity of the output. " \
                               "1 : only the error messages; " \
                               "2 : only the error and the warning messages; " \
                               "3 : all messages except debug messages; " \
                               "4 : all messages, including debug debug messages; ")

        self.add_argument('--version',
                          action='version',
                          version="{0} v. {1}".format(__projectname__, __version__),
                          help="show the version and exit")

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def explain_displayed_messages(verbosity):
        """
                CommandLineParser.explain_displayed_messages()
                ________________________________________________________________

                Return a string explaining which message will be displayed among
                debug, warning, (...) messages.
                ________________________________________________________________

                PARAMETER(S) :
                o verbosity     : (int)should be equal to ARGS.verbosity

                RETURNED VALUE    : (str)a string describing the displayed messages.
        """
        if verbosity == 4:
            return "all messages and the debugging messages"
        elif verbosity == 3:
            return "all messages except debugging messages"
        elif verbosity == 2:
            return "only the error and the warning messages"
        elif verbosity == 1:
            return "only the error messages"
        elif verbosity == 0:
            return "no message"
        else:
            return "Error : can interpret the 'verbosity' parameter"

    #///////////////////////////////////////////////////////////////////////////
    def get_args(self):
        """
                CommandLineParser.get_args()
                ________________________________________________________________

                Parse the command line arguments and return the argparse.Namespace
                object.

                ________________________________________________________________

                PARAMETER(S)    : no parameter

                RETURNED VALUE    : the argparse.Namespace object
        """
        return self.parse_args()

ARGS = None
