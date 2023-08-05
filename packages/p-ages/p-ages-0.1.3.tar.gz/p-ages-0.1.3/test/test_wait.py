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
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from pages.wait.wait import Wait, Repeat
from test.utils.mocks import MockedWebDriver


class WaitTest(unittest.TestCase):
    """
    Unit test for Wait class.
    """
    def test_set_time_out(self):
        wait = Wait(1).with_timeout(10)
        assert_that(wait._timeout, equal_to(10), 'timeout can be set')

    def test_set_poll_interval(self):
        wait = Wait(10).with_poll_interval(1)
        assert_that(wait._poll, equal_to(1), 'poll interval can be set')

    def test_set_driver(self):
        driver = MockedWebDriver()
        wait = Wait(10).with_driver(driver)
        assert_that(wait._driver.session_id, equal_to(driver.session_id))

    def test_repeat(self):
        assert_that(isinstance(Repeat(1), Wait), equal_to(True))

    def test_ignored_exceptions_can_be_not_iterable(self):
        wait = Wait(1, ignored_exceptions=FirstException)
        assert_that(wait._ignored_exceptions, equal_to((NoSuchElementException, FirstException)))

    def test_ignored_exceptions_can_be_iterable(self):
        wait = Wait(1).with_ignored_exceptions(FirstException, SecondException)
        assert_that(wait._ignored_exceptions, equal_to((NoSuchElementException, FirstException, SecondException)))

    def test_wait_until_gives_an_exceptions_for_a_non_callable(self):
        assert_that(calling(Wait(1).until_condition).with_args(function(), 'a non callable'), raises(TypeError))

    def test_wait_until_returns_evaluated_value(self):
        wait_until = Wait(1).until_condition(function, 'always true')
        assert_that(wait_until, equal_to('the value'))

    def test_wait_until_raises_TimeoutException(self):
        assert_that(calling(Wait(0).until_condition).with_args(always_false, 'always false'), raises(TimeoutException))


class FirstException(Exception):
    pass


class SecondException(Exception):
    pass


def function():
    return 'the value'


def always_false():
    return False
