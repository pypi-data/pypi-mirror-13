# This file is part of python-dialback.
#
# python-dialback is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-dialback is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-dialback.  If not, see <http://www.gnu.org/licenses/>.
import collections

class DialbackExcpetion(Exception):
    """ Dialback exception that all other dialback exceptions extend from

    This is a generic exception that could be raised when no other exception is
    appropriate, alike python's Exception class of which this extends. This also
    is what all other dialback exceptions extend from.
    """

    def __init__(self, error, section=None, *args, **kwargs):
        # If the section is an iterable it is an iterable of several sections
        if isinstance(section, collections.Iterable):
            # Convert the section numbers into strings for formatting
            section = tuple(str(s) for s in section)

            # Format it in "section1, ... & section-1" format
            section = "{0} & {1}".format(", ".join(section[:1]), section[0])

        # If the section isn't None, go ahead and add it to the end.
        if section is not None:
            error = "{error} (section(s) {section})".format(
                error=error,
                section=section
            )
        super(DialbackExcpetion, self).__init__(error, *args, **kwargs)

class DialbackValidationError(DialbackExcpetion):
    """ Raised when data does not validate

    This is raised anytime data given is invalid or missing. This extends from
    the DialbackExcpetion.
    """
    pass