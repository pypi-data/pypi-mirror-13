############################################################################
# Copyright 2015 Skyscanner Ltd                                            #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#    http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
import unittest

from hamcrest import assert_that, calling, raises, ends_with

from pages.traits import Trait


class TraitsTest(unittest.TestCase):
    """
    Unit test for Traits class.
    """
    def test_is_loaded(self):
        assert_that(calling(a_malformed_trait), raises(TypeError))

    def test_str(self):
        assert_that(a_trait().__str__(), ends_with('always present'))


def foo():
    pass


def a_malformed_trait():
    return Trait(foo(), 'a non callable condition')


def a_trait():
    return Trait(lambda: True, 'always present')
