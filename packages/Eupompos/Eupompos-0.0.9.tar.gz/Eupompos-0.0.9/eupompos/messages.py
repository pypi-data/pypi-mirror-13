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
        ❏Eupompos❏ eupompos/messages.py
        ________________________________________________________________________

        Messages emitted by the program : debug messages, warnings, errors, ...
        ________________________________________________________________________

        o Messages class
        o MSG instance
"""
# something's wrong with the way pylint understands the import statement :
# pylint: disable=import-error

import linecache
import sys

import eupompos.settings as settings
from eupompos.cmdlineparser import CommandLineParser
from eupompos.filetools import normpath

################################################################################
class Messages(object):
    """
        Messages class.
        ________________________________________________________________________

        Use this class to display various messages and to count warning and
        error messages.

        Unique instance : MSG (see at the end of the file)
        ________________________________________________________________________

        class attributes : -

        instance attributes  :

            o warnings_number    : (int) number of warning messages displayed
            o errors_number      : (int) number of error messages displayed

        class methods :

            o __init__()
            o debug()
            o error()
            o get_infos_about_the_exception()       [static]
            o msg()                                 [static]
            o warning()
            o welcome0()
            o welcome1()
        ________________________________________________________________________

        self.debug(), self.warning() and self.error() are based upon self.msg()

        See the --verbosity command line parameter.
    """

    #///////////////////////////////////////////////////////////////////////////
    def __init__(self):
        """
                Messages.__init__()
                ________________________________________________________________

                PARAMETER(S)    : no parameter

                RETURNED VALUE    : no RETURNED VALUE
        """
        self.warnings_number = 0
        self.errors_number = 0

    #///////////////////////////////////////////////////////////////////////////
    def debug(self, text):
        """
                Messages.debug()
                ________________________________________________________________

                version of self.msg() for debug messages.
                ________________________________________________________________

                PARAMETER       : (str)the text to be displayed.

                RETURNED VALUE    : no RETURNED VALUE
        """
        self.msg(text, 'debug')

    #///////////////////////////////////////////////////////////////////////////
    def error(self, text):
        """
                Messages.error()
                ________________________________________________________________

                version of self.msg() for error messages.
                increase self.errors_number
                ________________________________________________________________

                PARAMETER       : (str)the text to be displayed.

                RETURNED VALUE    : no RETURNED VALUE
        """
        self.errors_number += 1

        if settings.VERBOSITY < 4:
            self.msg("   " + text, 'error')
        else:
            self.msg(text + \
                     "\nPython exception : " + Messages.get_infos_about_the_exception(),
                     'error')

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def get_infos_about_the_exception(exception=None):
        """
                Messages.get_infos_about_the_exception()
                ________________________________________________________________

                return a string with some informations about the given exception :
                    exception name, filename, line number, line, error message .

                If exception if set to None, return the string "(no exception)" .
                ________________________________________________________________

                PARAMETER       : the exception to be analysed or None if no
                                  specific exception could be given.

                RETURNED VALUE    : (str)a string with the informations
        """
        if exception is None:
            return "(no exception)"

        _, exc_obj, traceback = sys.exc_info()
        frame = traceback.tb_frame
        lineno = traceback.tb_lineno
        _filename = frame.f_code.co_filename
        linecache.checkcache(_filename)
        line = linecache.getline(_filename, lineno, frame.f_globals)

        exception_str = ""
        if exception is not None:
            exception_str = "(exception {0}) ".format(type(exception))

        return '{0}in {1}#{2} -> "{3}" : {4}'.format(exception_str,
                                                     _filename,
                                                     lineno,
                                                     line.strip(),
                                                     exc_obj)

    #///////////////////////////////////////////////////////////////////////////
    @staticmethod
    def msg(text, level='normal'):
        """
                Messages.msg()
                ________________________________________________________________

                Display a message to the console according to its level of
                importance and to VERBOSITY.

                ________________________________________________________________

                PARAMETERS :
                o text  : (str) the text to be displayed
                o level : (str) 'debug' or 'normal' or 'warning' or 'error'

                RETURNED VALUE : no RETURNED VALUE
        """
        if settings.VERBOSITY == 4 or \
           (settings.VERBOSITY == 3 and level not in ('debug',)) or \
           (settings.VERBOSITY == 2 and level not in ('debug', 'normal')) or \
           (settings.VERBOSITY == 1 and level not in ('debug', 'normal', 'warning')):
            print(text)

    #///////////////////////////////////////////////////////////////////////////
    def warning(self, text):
        """
                Messages.warning()
                ________________________________________________________________

                version of self.msg() for warning messages.
                increase self.warnings_number
                ________________________________________________________________

                PARAMETER       : (str)the text to be displayed.

                RETURNED VALUE    : no RETURNED VALUE
        """
        self.warnings_number += 1
        self.msg(text, 'warning')

    #///////////////////////////////////////////////////////////////////////////
    def welcome0(self):
        """
                Messages.welcome0()
                ________________________________________________________________

                Display a welcome message.
                ________________________________________________________________

                PARAMETER(S)    : no parameter

                RETURNED VALUE    : no RETURNED VALUE
        """
        self.msg("{0}, v.{1}".format(settings.PROJECT_NAME,
                                     settings.PROJECT_VERSION))

    #///////////////////////////////////////////////////////////////////////////
    def welcome1(self):
        """
                Messages.welcome1()
                ________________________________________________________________

                Display some informations.
                ________________________________________________________________

                PARAMETER(S)    : no parameter

                RETURNED VALUE    : no RETURNED VALUE
        """
        self.msg("source path : \"{0}\" " \
                 "(fullpath: \"{1}\")".format(settings.SOURCEPATH,
                                              normpath(settings.SOURCEPATH)))

        self.msg("config file : \"{0}\" " \
                 "(fullpath: \"{1}\")".format(settings.CONFIGFILENAME,
                                              normpath(settings.CONFIGFILENAME)))

        explanations_about_msg = CommandLineParser.explain_displayed_messages(settings.VERBOSITY)
        self.msg("messages to be displayed : {0}".format(explanations_about_msg))

        self.msg("")

MSG = Messages()
