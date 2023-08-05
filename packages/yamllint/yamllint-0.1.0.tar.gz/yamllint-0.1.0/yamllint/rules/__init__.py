# -*- coding: utf-8 -*-
# Copyright (C) 2016 Adrien Vergé
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from yamllint.rules import (
    colon,
    document_end,
    document_start,
    empty_lines,
    hyphen,
    indentation,
    line_length,
    new_line_at_end_of_file,
    new_lines,
    trailing_spaces,
)

colon

_RULES = {
    colon.ID: colon,
    document_end.ID: document_end,
    document_start.ID: document_start,
    empty_lines.ID: empty_lines,
    hyphen.ID: hyphen,
    indentation.ID: indentation,
    line_length.ID: line_length,
    new_line_at_end_of_file.ID: new_line_at_end_of_file,
    new_lines.ID: new_lines,
    trailing_spaces.ID: trailing_spaces,
}


def get(id):
    if id not in _RULES:
        raise ValueError('no such rule: "%s"' % id)

    return _RULES[id]
