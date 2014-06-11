# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import unittest

from nose.tools import eq_


class TestTest(unittest.TestCase):

    def test_clean_no_errors(self):
        code = 0
        eq_(code, 0)

 
