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

from yamllint.rules.common import spaces_after, spaces_before


ID = 'brackets'
TYPE = 'token'
CONF = {'min-spaces-inside': int,
        'max-spaces-inside': int}


def check(conf, token, prev, next):
    if isinstance(token, yaml.FlowSequenceStartToken):
        problem = spaces_after(token, prev, next,
                               min=conf['min-spaces-inside'],
                               max=conf['max-spaces-inside'],
                               min_desc='too few spaces inside brackets',
                               max_desc='too many spaces inside brackets')
        if problem is not None:
            yield problem

    elif (isinstance(token, yaml.FlowSequenceEndToken) and
            (prev is None or
             not isinstance(prev, yaml.FlowSequenceStartToken))):
        problem = spaces_before(token, prev, next,
                                min=conf['min-spaces-inside'],
                                max=conf['max-spaces-inside'],
                                min_desc='too few spaces inside brackets',
                                max_desc='too many spaces inside brackets')
        if problem is not None:
            yield problem
