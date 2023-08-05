import unittest

from hamcrest import assert_that, equal_to
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command

from pages.page import Page
from test.utils.mocks import MockedWebDriver


class ElementWithTraitsTest(unittest.TestCase):
    """
    Unit test for Page class.
    """

    def test_can_load(self):
        driver = MockedWebDriver()

        driver.set_expected_command(Command.GET, {'url': 'http://www.example.com', 'sessionId': driver.session_id})
        ATestPage(driver).load()
        assert_that(driver.has_fulfilled_expectations(), equal_to(True))

    def test_has_element_with_locator(self):
        driver = MockedWebDriver()
        driver.set_expected_command(Command.FIND_ELEMENTS, {"using": By.ID, "sessionId": driver.session_id,
                                                            "value": 'a_locator'})

        ATestPage(driver).has_element_with_locator([By.ID, 'a_locator'])

        assert_that(driver.has_fulfilled_expectations(), equal_to(True), "page should check if it element is present")


class ATestPage(Page):
    def __init__(self, driver):
        super(ATestPage, self).__init__(driver, 'a_test_page')
        self.driver = driver

    def load(self):
        self.driver.get('http://www.example.com')
