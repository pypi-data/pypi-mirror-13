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
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from pages.standard_components.label import Label

from test.utils.mocks import MockedWebDriver


class LabelTest(unittest.TestCase):
    """
    Unit test for Label class.
    """
    def __init__(self, methodName='runTest'):
        super(LabelTest, self).__init__(methodName)
        self.driver = MockedWebDriver()

    def test_get_for_attribute(self):
        self.driver.set_dom_element([By.ID, 'label'], return_values=[{'name': {'for': 'attr'}}])
        self.driver.set_expected_command(Command.GET_ELEMENT_ATTRIBUTE, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'label'])})
        #
        image_src = Label(self.driver, 'label', [By.ID, 'label']).get_for_attribute()
        #
        assert_that(image_src, equal_to('attr'), 'attribute for image should match')
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True))
