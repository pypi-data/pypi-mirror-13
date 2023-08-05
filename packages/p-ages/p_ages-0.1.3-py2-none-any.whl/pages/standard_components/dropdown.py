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
from pages.ui_component import UIComponent


class Dropdown(UIComponent):
    """
    Simplistic implementation of a dropdown. It does not include (for now) wait mechanism for options expansion.
    """
    def __init__(self, driver, name='dropdown', locator=None):
        UIComponent.__init__(self, driver, name, locator)

    def select_option_by_name(self, option_name):
        self.locate().click()
        self.locate().find_element_by_xpath("./option[text()='{name}']".format(name=option_name)).click()

    def select_option_by_value(self, option_value):
        self.locate().click()
        option = self.locate().find_element_by_xpath("./option[@value='{value}']".format(value=option_value))
        option.click()

    def get_option_labels(self):
        return [option.text for option in self.locate().find_elements_by_xpath(".//option")]
