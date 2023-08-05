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
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from pages.ui_component import UIComponent
from pages.wait.wait import Repeat


class TextInput(UIComponent):

    def __init__(self, driver, name, locator=None):
        UIComponent.__init__(self, driver, name, locator)

    def clear(self):
        self.locate().clear()
        return self

    def focus(self):
        self.locate().click()
        Repeat(5, 0.5).until_condition(self._input_focused, "text input is in focus")
        return self

    def input_text(self, text):
        self.locate().send_keys(Keys.CLEAR)
        self.locate().send_keys(text)
        return self

    def input_text_with_keyboard_emulation(self, text):
        """
            Works around the problem of emulating user interactions with text inputs.
            Emulates a key-down action on the first char of the input. This way, implementations which
            require key-down event to trigger auto-suggest are testable.
            Then the chains sends the rest of the text and releases the key.
        """
        ActionChains(self.driver).key_down(text).key_up(Keys.CONTROL).perform()

    def get_placeholder_text(self):
        return self.locate().get_attribute('placeholder')

    def get_current_value(self):
        return self.locate().get_attribute('value')

    def _input_focused(self):
        self.locate().click()
        return self.driver.switch_to.active_element == self.locate()
