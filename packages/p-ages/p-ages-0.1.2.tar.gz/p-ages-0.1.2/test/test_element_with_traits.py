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

from hamcrest import equal_to, assert_that, raises, calling
from selenium.common.exceptions import TimeoutException

from pages.element_with_traits import ElementWithTraits
from pages.exceptions import IllegalStateException


class ElementWithTraitsTest(unittest.TestCase):
    """
    Unit test for ElementWithTraits class.
    """

    def test_can_wait_until_traits_are_loaded(self):
        element = ElementWithTraits('an_element').add_trait(lambda: True, 'always present')
        assert_that(element.wait_until_loaded(5, 1), equal_to(element))

    def test_raises_timeout_when_traits_do_not_load(self):
        element = ElementWithTraits('an_element').add_trait(lambda: False, 'never loading')
        assert_that(calling(element.wait_until_loaded).with_args(1, 0.5), raises(TimeoutException))

    def test_raises_exception_when_there_are_no_traits(self):
        element = ElementWithTraits('an_element')
        assert_that(calling(element.wait_until_loaded).with_args(1, 0.5),
                    raises(IllegalStateException))

    def test_lazy_evaluation(self):
        element = get_element_with_traits_and_lazy_evaluation(True)

        assert_that(element.evaluate_traits(), equal_to(['never true #1']))

    def test_eager_evaluation(self):
        element = get_element_with_traits_and_lazy_evaluation(False)

        assert_that(element.evaluate_traits(), equal_to(['never true #1', 'never true #2']))


def get_element_with_traits_and_lazy_evaluation(value):
        an_element = ElementWithTraits('an element')
        if not value:
            an_element.with_eager_evaluation()
        an_element.add_trait(lambda: False, 'never true #1')
        an_element.add_trait(lambda: False, 'never true #2')

        return an_element
