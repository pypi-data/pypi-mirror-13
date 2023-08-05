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


class Trait(object):
    """
    A trait is an abstraction of the condition that must be verified for an element to be ready.
    """
    def __init__(self, condition, description):
        """
        :param condition: it is a callable object that must return a boolean.
        :param description: it is a short description of the condition. E.g. 'page has logo', 'table has 10 elements'
        """
        if not hasattr(condition, '__call__'):
            raise TypeError("condition should be callable")
        self.condition = condition
        self.description = description

    def __str__(self):
        return "condition: " + str(self.condition) + ", " + self.description
