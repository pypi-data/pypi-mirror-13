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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.command import Command

from pages.standard_components.textinput import TextInput
from test.utils.mocks import MockedWebDriver


class TextIputTest(unittest.TestCase):
    """
    Unit test for TextInput class.
    """

    def __init__(self, methodName='runTest'):
        super(TextIputTest, self).__init__(methodName)
        self.driver = MockedWebDriver()

    def test_clear(self):
        self.driver.set_dom_element([By.ID, 'input'])
        self.driver.set_expected_command(Command.CLEAR_ELEMENT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'input'])})
        #
        TextInput(self.driver, 'input', [By.ID, 'input']).clear()
        #
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "clearing text input should fulfill test expectations")

    def test_focus(self):
        self.driver.set_dom_element([By.ID, 'input'])
        self.driver.set_expected_command(Command.CLICK_ELEMENT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'input'])})
        self.driver.set_expected_command(Command.CLICK_ELEMENT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'input'])})
        self.driver.set_expected_command(Command.GET_ACTIVE_ELEMENT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'input'])})
        #
        TextInput(self.driver, 'input', [By.ID, 'input']).focus()
        #
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "focusing on element should fulfill expectations")

    def test_input_text(self):
        self.driver.set_dom_element([By.ID, 'input'])
        self.driver.set_expected_command(Command.SEND_KEYS_TO_ELEMENT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'input']),
                                                                        'value': Keys.CLEAR})
        self.driver.set_expected_command(Command.SEND_KEYS_TO_ELEMENT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'input']),
                                                                        'value': 'text'})
        #
        TextInput(self.driver, 'input', [By.ID, 'input']).input_text('text')
        #
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "inputting text should fulfill expectations")

    def test_get_placeholder_text(self):
        self.driver.set_dom_element([By.ID, 'input'], return_values=[{'name': {'placeholder': 'placeholder text'}}])
        self.driver.set_expected_command(Command.GET_ELEMENT_ATTRIBUTE, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'input'])})
        #
        text = TextInput(self.driver, 'input', [By.ID, 'input']).get_placeholder_text()
        #
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "getting placeholder value should fulfill expectations")
        assert_that(text, equal_to('placeholder text'))

    def test_get_current_value(self):
        self.driver.set_dom_element([By.ID, 'input'], return_values=[{'name': {'value': 'current value'}}])
        self.driver.set_expected_command(Command.GET_ELEMENT_ATTRIBUTE, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'input'])})
        #
        text = TextInput(self.driver, 'input', [By.ID, 'input']).get_current_value()
        #
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "getting current value should fulfill expectations")
        assert_that(text, equal_to('current value'))

    def test_input_text_with_keyboard_emulation(self):
        self.driver.set_dom_element([By.ID, 'input'])
        self.driver.set_expected_command(Command.SEND_KEYS_TO_ACTIVE_ELEMENT,
                                         {'sessionId': self.driver.session_id,
                                          'id': self.driver.get_id_for_stored_element([By.ID, 'input']),
                                          'value': 'text to send'})
        self.driver.set_expected_command(Command.SEND_KEYS_TO_ACTIVE_ELEMENT,
                                         {'sessionId': self.driver.session_id,
                                          'id': self.driver.get_id_for_stored_element([By.ID, 'input']),
                                          'value': Keys.CONTROL})
        #
        TextInput(self.driver, 'input', [By.ID, 'input']).input_text_with_keyboard_emulation('text to send')
        #
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "getting current value should fulfill expectations")
