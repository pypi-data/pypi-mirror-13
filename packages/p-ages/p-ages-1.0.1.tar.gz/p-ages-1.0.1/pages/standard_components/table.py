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

from pages.element_with_language import ElementWithLanguage
from pages.ui_component import UIComponent


class Table(UIComponent, ElementWithLanguage):
    """
    Generic model of a table.
    E.g.
    <table class="atable">
        <tbody>
            <tr>...
            ...
            <tr>...
        <\tbody>
    <\table>
    How to use it:
    table = Table(driver, "table", [By.XPATH, ".//tr"], Item, "item", [By.XPATH, "//table[@class='atable']"])
    table.get_items()

    Notice Item must be a subclass of UIComponent.
    """

    def __init__(self, driver, table_name, item_relative_locator, item_class, item_name, table_locator=None):
        UIComponent.__init__(self, driver, table_name, table_locator)
        ElementWithLanguage.__init__(self)
        if not issubclass(item_class, UIComponent):
            raise TypeError("{0} is not subtype of UIComponent".format(item_name))
        self._item_relative_locator = item_relative_locator
        self._item_class = item_class
        self._item_name = item_name

    def get_items(self):
        if self._item_has_language():
            return [self._item_class(self.driver, "{0} #{1}".format(self._item_name, index)).from_web_element(item)
                        .with_language(self.language) for index, item in
                    self._enumerate_table_elements(self.locate())]
        else:
            return [self._item_class(self.driver, "{0} #{1}".format(self._item_name, index)).from_web_element(item) for
                    index, item in self._enumerate_table_elements(self.locate())]

    def _enumerate_table_elements(self, table):
        by, locator = self._item_relative_locator
        return enumerate(table.find_elements(by=by, value=locator))

    def _item_has_language(self):
        return issubclass(self._item_class, ElementWithLanguage)
