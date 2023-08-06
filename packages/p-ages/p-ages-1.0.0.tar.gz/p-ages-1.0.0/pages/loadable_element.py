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
from abc import ABCMeta, abstractmethod

from pages.element_with_traits import ElementWithTraits


class LoadableElement(ElementWithTraits):
    """
    Abstract class defining a generic loadable element.
    """

    __metaclass__ = ABCMeta

    def __init__(self, driver, name):
        ElementWithTraits.__init__(self, name)
        self.driver = driver

    @abstractmethod  # pragma: no cover
    def load(self):
        """
        Load component through WebDriver API.
        Usage:
            implement action and return an instance of the class so to allow chaining.
            self.__driver__.get("www.example.com")
            return self
        :return: an instance of the class.
        """

    def is_loaded(self):
        return self.has_all_traits()
