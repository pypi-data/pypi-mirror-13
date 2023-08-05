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

import unittest

import yaml

from yamllint.config import parse_config
from yamllint.errors import LintProblem
from yamllint import lint


class RuleTestCase(unittest.TestCase):
    def build_fake_config(self, conf):
        if conf is None:
            conf = {}
        else:
            conf = yaml.safe_load(conf)
        conf = {'extends': 'default',
                'rules': conf}
        return parse_config(yaml.safe_dump(conf))

    def check(self, source, conf, line=None, column=None, **kwargs):
        expected_problems = []
        for key in kwargs:
            assert key.startswith('problem')
            expected_problems.append(
                LintProblem(kwargs[key][0], kwargs[key][1], rule=self.rule_id))
        expected_problems.sort()

        real_problems = list(lint(source, self.build_fake_config(conf)))
        self.assertEqual(real_problems, expected_problems)
