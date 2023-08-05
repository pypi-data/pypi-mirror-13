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

from hamcrest import assert_that, equal_to

from pages.loadable_element import LoadableElement
from test.utils.mocks import MockedWebDriver


class LoadableElementTest(unittest.TestCase):
    """
    Unit test for LoadableElement class.
    """

    def test_is_loaded(self):
        driver = MockedWebDriver()

        element = ALoadableElement(driver).load()
        assert_that(element.is_loaded(), equal_to(True), 'when traits are present element is_loaded() returns True')


class ALoadableElement(LoadableElement):
    def __init__(self, driver):
        super(ALoadableElement, self).__init__(driver, 'loadable_element')
        self.driver = driver
        self.add_trait(lambda: True, 'always present')

    def load(self):
        self.driver.get('http://www.example.com')
        return self
