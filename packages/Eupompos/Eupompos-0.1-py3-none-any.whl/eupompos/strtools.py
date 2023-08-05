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
        ❏Eupompos❏ ./eupompos/strtools.py
        ________________________________________________________________________

        Tools to be used with strings objects.
        ________________________________________________________________________

        o add_prefix_to_lines()
        o remove_final_newlinechars()
        o rm_spaces()
"""

################################################################################
def add_prefix_to_lines(_lines, _prefix):
    """
            add_prefix_to_lines()
            ____________________________________________________________________

            Add a prefix to each line in _lines.

                e.g. :
                        ["abc", "def"] -> ["PREFIXabc", "PREFIXdef"]
            ____________________________________________________________________

            PARAMETERS :
                o _lines        : a list of (str)lines
                o _prefix       : (str)the prefix to be added

            RETURNED VALUE :
                o a list of strings
    """
    res = []

    for line in _lines:
        res.append(_prefix+line)

    return res

################################################################################
def remove_final_newlinechars(_line):
    """
            remove_final_newlinechars()
            ____________________________________________________________________

            Remove any "new line" character at the end of line and return the
            resulting string.
            ____________________________________________________________________

            PARAMETERS :
                o _line         : the source line

            RETURNED VALUE :
                o (str)the expected string.
    """
    if _line.endswith("\r\n"):
        return _line[:-2]
    elif _line.endswith("\n"):
        return _line[:-1]
    elif _line.endswith("\r"):
        return _line[:-1]
    else:
        return _line

################################################################################
def rm_initial_spaces(_lines):
    """
            rm_initial_spaces()
            ____________________________________________________________________

            Find the minimal number of spaces at the beginning of the _lines
            and remove this number of spaces in every line.
            ____________________________________________________________________

            PARAMETERS :
                o _lines        : a list of (str)lines

            RETURNED VALUE :
                o a list of strings.
    """
    if len(_lines) == 0:
        return _lines

    # number of space characters to be deleted at the beginning of the lines :
    spaces_nbr = None

    for line in _lines:
        if spaces_nbr is None:
            spaces_nbr = len(line) - len(line.lstrip())
        else:
            spaces_nbr = min(spaces_nbr, len(line) - len(line.lstrip()))

    res = []
    for line in _lines:
        res.append(line[spaces_nbr:])

    return res
