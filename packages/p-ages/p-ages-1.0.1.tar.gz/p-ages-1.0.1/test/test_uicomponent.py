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

from hamcrest import equal_to, assert_that, is_not, raises
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webelement import WebElement

from pages.ui_component import UIComponent
from test.utils.mocks import MockedWebElement, MockedWebDriver


class UiComponentTest(unittest.TestCase):
    """
    Unit test for UiComponent class.
    """

    def __init__(self, methodName='runTest'):
        super(UiComponentTest, self).__init__(methodName)
        self.driver = MockedWebDriver()

    def test_component_can_be_created_from_web_element(self):
        component = UIComponent(self.driver, 'a component', [By.ID, 'theId'])
        a_web_element = WebElement(None, '')
        ##
        component.from_web_element(a_web_element)
        ##
        assert_that(component.locate(), equal_to(a_web_element),
                    "fromWebElement should store a reference to passed WebElement")

    def test_raise_error_when_trying_to_construct_from_wrong_type(self):
        def construct_from_foo():
            driver = MockedWebDriver()
            return UIComponent(driver, 'a component').from_web_element(Foo())
        assert_that(construct_from_foo, raises(TypeError), "passing unexpected type should causes exception")

    def test_web_element_is_stored_with_caching(self):
        component = UIComponent(self.driver, 'a component', [By.ID, 'theid'])
        self.driver.set_dom_element([By.ID, 'theid'])
        element_first_time = component.cache().locate()
        ##
        self.driver.reset_dom_elements()
        self.driver.set_dom_element([By.ID, 'theid'])
        element_second_time = component.locate()
        ##
        assert_that(element_first_time, equal_to(element_second_time),
                    "when cached web_element() should return always the same WebElement object")

    def test_web_element_is_evaluated_every_time_without_caching(self):
        component = UIComponent(self.driver, 'a component', [By.ID, 'theid'])
        self.driver.set_dom_element([By.ID, 'theid'])
        element_first_time = component.locate()
        ##
        self.driver.reset_dom_elements()
        self.driver.set_dom_element([By.ID, 'theid'])
        element_second_time = component.locate()
        ##
        assert_that(element_first_time, is_not(equal_to(element_second_time)),
                    "when cached web_element() should return always the same WebElement object")

    def test_component_is_found_when_has_all_traits(self):
        component = UIComponent(self.driver, 'a_component', [By.ID, 'an_id'])
        ##
        component.add_trait(lambda: True, 'always true')
        ##
        assert_that(component.is_found(), equal_to(True), "component should be found when all traits are present")

    def test_component_is_not_found_when_trait_raises_an_exception(self):
        component = UIComponent(self.driver, 'a_component', [By.ID, 'an_id'])
        ##
        component.add_trait(raise_exception, 'always true')
        ##
        assert_that(component.is_found(), equal_to(False),
                    "component should not be found when evaluating traits throws an exception")

    def test_is_present(self):
        self.driver.set_dom_element([By.ID, 'an_id'])
        component = UIComponent(self.driver, 'a_component', [By.ID, 'an_id'])

        component.is_present()

        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "component should be able to locate element it is scope")

    def test_component_can_be_clicked(self):
        self.driver.set_dom_element([By.ID, 'an_id'])

        self.driver.set_expected_command(Command.CLICK_ELEMENT, {'sessionId': self.driver.session_id,
                                         'id': self.driver.get_id_for_stored_element([By.ID, 'an_id'])})

        component = UIComponent(self.driver, 'a_component', [By.ID, 'an_id'])
        ##
        component.click()
        ##
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "clicking on component should result in click command")

    def test_component_can_be_hovered(self):
        self.driver.set_dom_element([By.ID, 'an_id'])
        self.driver.set_expected_command(Command.MOVE_TO, {'sessionId': self.driver.session_id,
                                                           'element': self.driver.get_id_for_stored_element(
                                                               [By.ID, 'an_id'])})
        component = UIComponent(self.driver, 'a_component', [By.ID, 'an_id'])
        ##
        component.hover()
        ##
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "clicking on component should result in hoover command")

    def test_has_element(self):
        self.driver.set_dom_element([By.ID, 'an_id'])
        component = UIComponent(self.driver, 'a_component', [By.ID, 'an_id'])
        self.driver.set_dom_element([By.XPATH, './/option'], parent_id=[By.ID, 'dropdownlocator'], children=1,
                                    return_values=[])

        self.driver.set_expected_command(Command.FIND_CHILD_ELEMENTS, {'using': By.ID, 'value': self.driver.
                                         get_id_for_stored_element([By.ID, 'an_id']),
                                         'id': 'id', "sessionId": self.driver.session_id})
        ##
        component.has_element([By.ID, 'another_id'])
        ##
        assert_that(self.driver.has_fulfilled_expectations(), equal_to(True),
                    "component should be able to locate element it is scope")

    def test_can_cache_element(self):
        component = UIComponent(self.driver, 'a_component', [By.ID, 'an_id'])
        component.cache()
        cached_element = MockedWebElement(self.driver, 'another_id')
        ##
        component._cache_web_element(cached_element)
        ##
        assert_that(component.locate(), equal_to(cached_element))


def raise_exception():
    raise NoSuchElementException


class Foo():
    pass
