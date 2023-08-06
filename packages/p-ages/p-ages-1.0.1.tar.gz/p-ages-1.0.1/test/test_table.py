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

from hamcrest import assert_that, equal_to, calling, raises
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command

from pages.element_with_language import ElementWithLanguage
from pages.standard_components.table import Table
from pages.ui_component import UIComponent
from test.utils.mocks import MockedWebDriver


class TableTest(unittest.TestCase):
    """
    Unit test for Table class.
    """

    def __init__(self, methodName='runTest'):
        super(TableTest, self).__init__(methodName)
        self.driver = MockedWebDriver()

    def setUp(self):
        self.driver.reset_dom_elements()

    def test_get_items_with_language(self):
        self.driver.set_dom_element([By.ID, 'table'])
        self.driver.set_dom_element([By.XPATH, './/tr'], parent_id=[By.ID, 'table'], children=4,
                                    return_values=[{'text': 'first'}, {'text': 'second'}, {'text': 'third'},
                                                   {'text': 'fourth'}])
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                                                    'id': self.driver.get_id_for_stored_element(
                                                                        [By.XPATH, './/tr'], 1)})
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                                                    'id': self.driver.get_id_for_stored_element(
                                                                        [By.XPATH, './/tr'], 2)})
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                                                    'id': self.driver.get_id_for_stored_element(
                                                                        [By.XPATH, './/tr'], 3)})
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                                                    'id': self.driver.get_id_for_stored_element(
                                                                        [By.XPATH, './/tr'], 4)})

        #
        items = Table(self.driver, 'table', [By.XPATH, './/tr'], ItemWithLanguage, 'item', [By.ID, 'table']).get_items()
        labels = [i.get_text() for i in items]

        assert_that(labels, equal_to(['first', 'second', 'third', 'fourth']),
                    "It should retrieve labels from stored elements")
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "exercising get_items should result in calling Command.GET_ELEMENT_TEXT a number of times.")

    def test_detects_wrong_item_class(self):
        assert_that(calling(Table).with_args(self.driver, 'table', [By.ID, './/tr'], NonUiComponentItem, 'item',
                                             [By.ID, 'table']), raises(TypeError))

    def test_get_items_without_language(self):
        self.driver.set_dom_element([By.ID, 'table'])
        self.driver.set_dom_element([By.XPATH, './/tr'], parent_id=[By.ID, 'table'], children=4,
                                    return_values=[{'text': 'first'}, {'text': 'second'}, {'text': 'third'},
                                                   {'text': 'fourth'}])
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                                                    'id': self.driver.get_id_for_stored_element(
                                                                        [By.XPATH, './/tr'], 1)})
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                                                    'id': self.driver.get_id_for_stored_element(
                                                                        [By.XPATH, './/tr'], 2)})
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                                                    'id': self.driver.get_id_for_stored_element(
                                                                        [By.XPATH, './/tr'], 3)})
        self.driver.set_expected_command(Command.GET_ELEMENT_TEXT, {'sessionId': self.driver.session_id,
                                                                    'id': self.driver.get_id_for_stored_element(
                                                                        [By.XPATH, './/tr'], 4)})
        #
        items = Table(self.driver, 'table', [By.XPATH, './/tr'], Item, 'item', [By.ID, 'table']).get_items()
        #
        labels = [i.get_text() for i in items]

        assert_that(labels, equal_to(['first', 'second', 'third', 'fourth']),
                    "It should retrieve labels from stored elements")
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "exercising get_items should result in calling Command.GET_ELEMENT_TEXT a number of times.")


class Item(UIComponent):
    def __init__(self, driver, name):
        UIComponent.__init__(self, driver, name)

    def get_text(self):
        return self.locate().text


class ItemWithLanguage(Item, ElementWithLanguage):
    def __init__(self, driver, name):
        Item.__init__(self, driver, name)
        ElementWithLanguage.__init__(self)


class NonUiComponentItem(object):
    pass
