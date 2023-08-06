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
import logging
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException

POLL_FREQUENCY = 0.5
IGNORED_EXCEPTIONS = [NoSuchElementException]  # list of exceptions ignored during calls to the method
LAZY_EVALUATION = True  # Determines if traits should be all evaluated before returning.

logger = logging.getLogger(__name__)


class Wait(object):
    """
        Wait utils insipired to Selenium WebDriverWait. Main features are:
        - better logging and debugging of failing conditions
        - conditions not containing driver as parameter
        - until_condition() takes a callable condition which does not need to contain driver
        - until_traits_are_present() which is
    """

    def __init__(self, timeout, poll_frequency=POLL_FREQUENCY, ignored_exceptions=None, logger=None):
        self._timeout = timeout
        self._poll = poll_frequency
        self._driver = None

        # avoid the divide by zero
        if self._poll == 0:
            self._poll = POLL_FREQUENCY  # pragma: no cover
        exceptions = IGNORED_EXCEPTIONS
        if ignored_exceptions is not None:
            try:
                exceptions.extend(iter(ignored_exceptions))
            except TypeError:  # ignored_exceptions is not iterable
                exceptions.append(ignored_exceptions)
        self._ignored_exceptions = tuple(exceptions)

    def until_condition(self, condition, condition_description):
        """
        Waits until conditions is True or returns a non-None value.
        If any of the trait is still not present after timeout, raises a TimeoutException.
        """
        end_time = time.time() + self._timeout
        count = 1
        while True:
            try:
                if not hasattr(condition, '__call__'):
                    raise TypeError("condition is not callable")
                value = condition()
                if type(value) is bool and value is not False:
                    return value
                elif type(value) is not bool and value is not None:
                    return value
                else:
                    logger.debug("#" + str(count) + " - wait until " + condition_description)  # pragma: no cover
            except self._ignored_exceptions as ex:
                logger.debug("Captured {0} : {1}".format(str(ex.__class__).replace("<type '", "").replace("'>", ""),
                                                         str(ex)))  # pragma: no cover
            time.sleep(self._poll)
            count += 1
            if time.time() > end_time:  # pragma: no cover
                break
        raise TimeoutException(
            msg="condition <" + condition_description + "> was not true after " + str(self._timeout) + " seconds.")

    def until_traits_are_present(self, element_with_traits):
        """
        Waits until all traits are present.
        If any of the traits is still not present after timeout, raises a TimeoutException.
        """
        end_time = time.time() + self._timeout
        count = 1
        missing_traits_descriptions = None
        while True:
            missing_traits_descriptions = []
            try:
                missing_traits_descriptions = element_with_traits.evaluate_traits()
                if len(missing_traits_descriptions) == 0:
                    return True
                else:
                    logger.debug("#{0} - wait until all traits are present: <{1}>".format(str(count), '> <'.join(
                        missing_traits_descriptions)))
            except self._ignored_exceptions as ex:  # pragma: no cover
                logger.debug("Captured {0}: {1}".format(str(ex.__class__).replace("<type '", "").replace("'>", ""),
                                                        str(ex)))  # pragma: no cover
                pass  # pragma: no cover
            time.sleep(self._poll)
            count += 1
            if time.time() > end_time:
                break
        raise TimeoutException(
            msg="conditions " + '<' + '> <'.join(missing_traits_descriptions) + '>' + " not true after " + str(
                self._timeout) + " seconds.")

    def with_timeout(self, timeout):
        """
        Set timeout value.
        """
        self._timeout = timeout
        return self

    def with_poll_interval(self, poll_interval):
        """
        Set poll interval value.
        """
        self._poll = poll_interval
        return self

    def with_ignored_exceptions(self, *ignored_exceptions):
        """
        Set a list of exceptions that should be ignored inside the wait loop.
        """
        for exception in ignored_exceptions:
            self._ignored_exceptions = self._ignored_exceptions + (exception,)
        return self

    def with_driver(self, driver):
        self._driver = driver
        return self


class Repeat(Wait):
    def __init__(self, timeout, poll_frequency=POLL_FREQUENCY, ignored_exceptions=None):
        Wait.__init__(self, timeout, poll_frequency, ignored_exceptions)
