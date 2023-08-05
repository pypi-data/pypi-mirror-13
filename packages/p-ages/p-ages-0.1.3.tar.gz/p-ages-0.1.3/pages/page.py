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
from abc import abstractmethod, ABCMeta
import os

from pages.loadable_element import LoadableElement


DEFAULT_PAGE_TIMEOUT = 30
DEFAULT_PAGE_POLLING = 2


class Page(LoadableElement):
    """
    Abstraction of a generic web page.
    """
    __metaclass__ = ABCMeta

    def __init__(self, driver, name):
        LoadableElement.__init__(self, driver, name)
        self.timeout = int(os.getenv('PAGE_TIMEOUT', DEFAULT_PAGE_TIMEOUT))
        self.polling_time = int(os.getenv('PAGE_POLLING_TIME', DEFAULT_PAGE_POLLING))

    @abstractmethod
    def load(self):
        pass  # pragma: no cover

    def has_element_with_locator(self, locator):
        return len(self.driver.find_elements(locator[0], locator[1])) > 0
