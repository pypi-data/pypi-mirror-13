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

from pages.standard_components.dropdown import Dropdown
from test.utils.mocks import MockedWebDriver


class DropdownTest(unittest.TestCase):
    """
    Unit test for Dropdown class.
    """

    def __init__(self, methodName='runTest'):
        super(DropdownTest, self).__init__(methodName)
        self.driver = MockedWebDriver()

    def setUp(self):
        self.driver.reset_dom_elements()

    def test_dropdown_executes_select_option_by_name(self):
        self.driver.set_dom_elements([[By.ID, 'dropdownlocator'], [By.XPATH, "./option[text()='thename']"]])
        self.driver.set_expected_command(Command.CLICK_ELEMENT, {'sessionId': self.driver.session_id, 'id':
                                         self.driver.get_id_for_stored_element([By.ID, 'dropdownlocator'])})
        self.driver.set_expected_command(Command.CLICK_ELEMENT, {'sessionId': self.driver.session_id, 'id':
                                         self.driver.get_id_for_stored_element([By.XPATH,
                                                                                "./option[text()='thename']"])})
        #
        Dropdown(self.driver, 'dropdown', [By.ID, 'dropdownlocator']).select_option_by_name('thename')
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "fetching option labels should result in executing Comman.CLICK and Command.FIND_CHILD_ELEMENTS")

    def test_dropdown_executes_select_option_by_value(self):
        self.driver.set_dom_elements([[By.ID, 'dropdownlocator'], [By.XPATH, "./option[@value='anoption']"]])

        self.driver.set_expected_command(Command.CLICK_ELEMENT, {'sessionId': self.driver.session_id, 'id':
                                         self.driver.get_id_for_stored_element([By.ID, 'dropdownlocator'])})

        self.driver.set_expected_command(Command.CLICK_ELEMENT, {'sessionId': self.driver.session_id, 'id':
                                         self.driver.get_id_for_stored_element([By.XPATH,
                                                                                "./option[@value='anoption']"])})
        #
        Dropdown(self.driver, 'dropdown', [By.ID, 'dropdownlocator']).select_option_by_value('anoption')
        #
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "fetching option labels should result in executing Comman.CLICK and Command.FIND_CHILD_ELEMENTS")

    def test_dropdown_executes_get_options_label(self):
        self.driver.set_dom_element([By.ID, 'dropdownlocator'])
        self.driver.set_dom_element([By.XPATH, './/option'], parent_id=[By.ID, 'dropdownlocator'], children=4,
                                    return_values=[{'text': 'first'}, {'text': 'second'}, {'text': 'third'},
                                                   {'text': 'fourth'}])
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.XPATH, './/option'], 1)})
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.XPATH, './/option'], 2)})
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.XPATH, './/option'], 3)})
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.XPATH, './/option'], 4)})
        #
        labels = Dropdown(self.driver, 'dropdown', [By.ID, 'dropdownlocator']).get_option_labels()
        #
        assert_that(labels, equal_to(['first', 'second', 'third', 'fourth']),
                    "It should retrieve labels from stored elements")


class CannedElement:

    def __init__(self, locator, parent=False, children=0):
        self.locator = locator
        self.is_parent = parent
        if children and not parent:
            raise ValueError('cannot specify children number if parent is not set')
        self.children = children
