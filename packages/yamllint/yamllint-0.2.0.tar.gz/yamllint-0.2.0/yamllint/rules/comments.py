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


ID = 'comments'
TYPE = 'token'
CONF = {'require-starting-space': bool,
        'min-spaces-from-content': int}


def check(conf, token, prev, next):
    for comment in get_comments_between_tokens(token, next):
        if (conf['min-spaces-from-content'] != -1 and
                not isinstance(token, yaml.StreamStartToken) and
                comment.line == token.end_mark.line + 1 and
                comment.pointer - token.end_mark.pointer <
                conf['min-spaces-from-content']):
            yield LintProblem(comment.line, comment.column,
                              'too few spaces before comment')

        if (conf['require-starting-space'] and
                comment.pointer + 1 < len(comment.buffer) and
                comment.buffer[comment.pointer + 1] != ' ' and
                comment.buffer[comment.pointer + 1] != '\n'):
            yield LintProblem(comment.line, comment.column + 1,
                              'missing starting space in comment')
