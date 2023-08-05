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

from hamcrest import equal_to, assert_that

from pages.element_with_language import ElementWithLanguage


class ElementWithLanguageTest(unittest.TestCase):
    """
    Unit test for ElementWithLanguage class.
    """

    def __init__(self, methodName='runTest'):
        super(ElementWithLanguageTest, self).__init__(methodName)

    def test_component_can_be_created_from_web_element(self):
        ##
        element = ElementWithLanguage().with_language(ITALIAN)
        ##
        assert_that(element.language, equal_to(ITALIAN),
                    "element should store language")


class Language(object):

    def __init__(self, language_id, locale, country_id, enabled):
        self.language_id = language_id
        self.locale = locale
        self.country_id = country_id
        self.enabled = enabled


ITALIAN = Language("IT", "it-it", "IT", True)
