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

import yaml

from yamllint.errors import LintProblem
from yamllint.rules.common import get_comments_between_tokens


ID = 'comments-indentation'
TYPE = 'token'


def check(conf, token, prev, next):
    if prev is None:
        return

    token_indent = token.start_mark.column
    if isinstance(token, yaml.StreamEndToken):
        token_indent = 0

    skip_first = True
    if isinstance(prev, yaml.StreamStartToken):
        skip_first = False

    for comment in get_comments_between_tokens(prev, token,
                                               skip_first_line=skip_first):
        if comment.column != token_indent + 1:
            yield LintProblem(comment.line, comment.column,
                              'comment not intended like content')
