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
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from pages.element_with_traits import ElementWithTraits


class UIComponent(ElementWithTraits):
    """
        Base class representing a generic component in the DOM of a web page. It cannot be instantiated.
        The responsibility of this class is providing the lazy creation of a WebElement.
        This is done on calling the locate() method.

        Usage:
            Subclass, e.g. AnElement(UIComponent), and add traits to it.
            Construction can be done from a locator:
                super(AnElement, self).__init__(a_driver, a_locator)
            or from an already existing WebElement
                super(AnElement, self).__init__(a_driver).from_web_element(an_element)
    """

    def __init__(self, driver, name, locator=None):
        ElementWithTraits.__init__(self, name)
        self.driver = driver
        self.__locator = locator
        self.__web_element = None
        self.__cache = False

    def from_web_element(self, web_element):
        """
            Store reference to a WebElement instance representing the element on the DOM.
            Use it when an instance of WebElement has already been created (e.g. as the result of find_element) and
            you want to create a UIComponent out of it without evaluating it from the locator again.
            Returns an instance of the class.
        """
        if isinstance(web_element, WebElement) is not True:
            raise TypeError("web_element parameter is not of type WebElement.")
        self.__web_element = web_element
        return self

    def cache(self):
        """
            Disclaimer: Dangerous method. Use it only if you know what you are doing.
            Enable caching of the element after lazy evaluation.
            Use in case of elements which are not being updated as results of actions on the page.
            Usage:
                AComponent(a_driver, a_locator).cache()
            Returns an instance of the class.
        """
        self.__cache = True
        return self

    def locate(self):
        """
            Lazily locates the element on the DOM if the WebElement instance is not available already.
            Returns a WebElement object.
            It also caches the element if caching has been set through cache().
        """
        if self.__web_element is not None:
            return self.__web_element
        else:
            locator_type, locator_value = self.__locator
            element = self.driver.find_element(by=locator_type, value=locator_value)
            self._cache_web_element(element)  # cache the element if allowed
            return element

    def is_found(self):
        """
            Evaluates if the element can be found in the DOM.
        """
        try:
            return self.has_all_traits()
        except NoSuchElementException:
            return False

    def is_present(self):
        try:
            self.locate()
            return True
        except NoSuchElementException:  # pragma: no cover
            return False  # pragma: no cover

    def click(self):
        self.locate().click()

    def hover(self):
        ActionChains(self.driver).move_to_element(self.locate()).perform()

    def has_element(self, element_locator):
        """
        Helper method which tries to locate the element within the scope of the current UIComponent.
        :param element_locator: should be in the form of [By.<locator_type>, <locator>]. E.g. [By.ID, "q"]
        """
        return len(self.locate().find_elements(*element_locator)) > 0

    def _cache_web_element(self, element):
        if self.__cache is True:
            self.__web_element = element
