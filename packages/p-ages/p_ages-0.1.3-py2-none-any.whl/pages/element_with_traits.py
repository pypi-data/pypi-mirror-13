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

from selenium.common.exceptions import StaleElementReferenceException

from pages.exceptions import IllegalStateException
from pages.traits import Trait
from pages.wait.wait import Wait


DEFAULT_POLLING_TIME = 0.5
DEFAULT_TIMEOUT = 25


class ElementWithTraits(object):
    """
    Base class which defines a mechanism to address timing issues on waiting for loading of elements in a tests.
    A trait is a condition that must be verified for the element to be ready.
    """
    def __init__(self, name):
        self.name = name
        self.traits = []
        self.timeout = DEFAULT_TIMEOUT
        self.polling_time = DEFAULT_POLLING_TIME
        self.traits_eager_evaluation = False

    def add_trait(self, condition, description):
        self.traits.append(Trait(condition, description))
        return self

    def with_eager_evaluation(self):
        self.traits_eager_evaluation = True

    def wait_until_loaded(self, timeout=DEFAULT_TIMEOUT, polling_time=DEFAULT_POLLING_TIME):
        self.timeout = timeout
        self.polling_time = polling_time
        wait = Wait(self.timeout, self.polling_time)\
            .with_ignored_exceptions(StaleElementReferenceException)
        if len(self.traits) == 0:
            raise IllegalStateException("Element '{0}' has no traits".format(self.name))
        else:
            wait.until_traits_are_present(self)
            return self

    def has_all_traits(self):
        return len(self.evaluate_traits()) == 0

    def evaluate_traits(self):
        """
        Evaluates traits and returns a list containing the description of traits which are not true.
        Notice that if LAZY_EVALUATION is set to False all traits are evaluated before returning. Use this option
        only for debugging purposes.
        """
        return_value = []
        for trait in self.traits:
            if not trait.condition():
                if not self.traits_eager_evaluation:
                    return [trait.description]
                else:
                    return_value.append(trait.description)
        return return_value
