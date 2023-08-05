pages
=====

|BuildStatus| |CoverageStatus| |PyPI1| |PyPI2| |PyPI3|

*pages* is a lightweight Python library which helps in the creation of
readable and reliable page/component objects for UI tests.

It is been designed to ensure that timing issues will have zero impact
on your test results.

It is a wrapper around the Python WebDriver bindings, but the same ideas
(components, traits, ...) could be adapted to any other driver technology - 
including mobile.

Introduction
============

The most common problem when introducing automated UI-based testing in
continuous integration is the brittle nature of the tests. A false negative in a CI
pipeline is often cause of stress, fierce discussions (slip the build
through vs. hold it on failure analysis) and in some cases radical
changes of test strategies. However, the value of reliable UI tests is
undeniable, as they are the closest thing to real usage of a product.
Moreover, they exercise the stack from the front-end, thus representing a way
to test integration of the whole system. This is why automated UI tests
sit at the top of the well-known test pyramid: they are seen as
difficult to implement and expensive to maintain.

However, reliability of tests is normally a *design problem*.

*pages* offers a simple but effective framework to build robust page
objects for UI tests.

Installation
============

.. code:: bash

      pip install p-ages

Design
======

The design revolves around three key concepts:

-  the `Page <https://github.com/Skyscanner/pages/blob/master/pages/page.py>`_ class
-  page `traits <https://github.com/Skyscanner/pages/blob/master/pages/traits.py>`_
-  the `UIComponent <https://github.com/Skyscanner/pages/blob/master/pages/ui_component.py>`_ class

As usual, the best way to learn how to use it is to start coding.

Example
-------

We want to create UI tests for this page:
http://the-internet.herokuapp.com/login.

This is a login page that, on successful authentication, takes to a
secure area page. We want to write a test that loads the login page and
executes authentication. We will create two page objects. All the
examples are in the
`samples <https://github.com/Skyscanner/pages/tree/master/samples>`__
folder.

First step - test container
~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a first step, we will create a container where we instantiate the
driver.

.. code:: python

    class LoginTest(unittest.TestCase):

        def setUp(self):
            self.driver = WebDriver()

        def test_can_login(self):
            pass

Second step - test implementation top-down
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Load the page, enter credentials and assert that the secure area page is
loaded. In code this becomes:

.. code:: python

    class LoginTest(unittest.TestCase):

        def setUp(self):
            self.driver = WebDriver()

        def test_can_login(self):
            login_page = LoginPage(self.driver).load().wait_until_loaded()

            secure_area_page = login_page.login('tomsmith', 'SuperSecretPassword!')

            assert_that(secure_area_page, is_loaded().with_timeout(PAGE_LOADING_TIMEOUT)
                        .with_polling(POLLING_INTERVAL))

Notice how the LoginPage needs only a reference to the driver that we have
created in the setUp. We know the API already, so we are adding method
calls to load() and wait\_until\_loaded(). However, this will be
explained in the next steps.

Third step - loading the Login page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Login page will extend the Page base class from our framework. One
requirement is that load(), which is abstract, has to be defined.
Moreover, since we are chaining other methods, load() has to return an
instance of the class.

.. code:: python

    class LoginPage(Page):

        def __init__(self, driver):
            Page.__init__(driver, 'Login page')

        def load(self):
            self.driver.get(LOGIN_PAGE_URL)
            return self

Fourth step - adding traits
~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Traits* are the conditions that have to be verified for the page to be
in the loaded state. In our case, the page has user text input, password
text input and submit button, since those are the elements we are going to interact with.
We'll start by defining three private methods to check the presence of
those elements.

.. code:: python

        def _has_username_input(self):
            return TextInput(self.driver, 'username', [By.ID, 'username']).is_present()

        def _has_password_input(self):
            return TextInput(self.driver, 'password', [By.ID, 'password']).is_present()

        def _has_submit_button(self):
            return Button(self.driver, 'submit', [By.XPATH, "//button[@type = 'submit']"]).is_present()

We can now add *traits* to the page under test. Let's add them to
the \_\_init\_\_().

.. code:: python

        def __init__(self, driver):
            Page.__init__(self, driver, 'Login page')
            self.add_trait(self._has_username_input, 'has username')
            self.add_trait(self._has_password_input, 'has password')
            self.add_trait(self._has_submit_button, 'has submit button')

Notice how add\_trait() takes as first parameter the method name. In
other words, it accepts only a callable. For instance, you may pass
a lambda to it. The second parameter is the short description of the
trait, used for logging.

Finally, notice how the three traits we chose are the elements that
need to be ready for the interactions we are going to have with the
page. While these three traits are verified, other parts of the page may
still be loading. While this should not be a problem for the safety of this test,
in general great care should be taken to select traits so that tests do not interact
with parts of the DOM which have not finished loading.

Fifth step - logging in and returning secure area page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On successful login, the secure area page should be returned. This is done
in the login\_user() method. Notice that we have refactored some of the
previous code for better reuse.

.. code:: python

        def login_user(self, username, password):
            self._user_name().input_text(username)
            self._password().input_text(password)
            self._submit_button().click()
            return SecureAreaPage(self.driver)

Sixth step - Secure Area Page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, we need to implement the return page. Similarly to the login
page:

.. code:: python

    class SecureAreaPage(Page):

        def __init__(self, driver):
            Page.__init__(self, driver, 'Secure area page')
            self.add_trait(self._has_logout_button, 'has logout button')

        def load(self):
            raise NotLoadablePageException('{0} cannot be loaded'.format(self.name))

        def _has_logout_button(self):
            return Button(self.driver, [By.XPATH, "//button[@href='/logout']"]).is_present()

Notice how we did not implement load(), since the secure area page is not
loadable from a URL.

Page objects
------------

In the previous example, we have seen how simple it is to implement page
objects and create tests with them. In essence, all we need to do is:

* extend the Page class
* implement the load() method
* add traits to the page

As a final (golden) rule, every method which models a user interaction
and results in a page load has to return a page object of the target page.
The simplest case is load() itself.

The benefit of building a page from the Page class is that, after proper
definition of traits, we can rely on wait\_until\_loaded() to reliably
pause the test execution *just enough* to allow the page to load.

.. code:: python

    login_page = LoginPage(self.driver).load().wait_until_loaded()

Page traits
-----------

Disclaimer: Traits we define here are not "class traits".

*A Trait is an abstraction of the condition that must be verified for an
element to be ready.* As shown in the example above, adding traits is
extremely simple. The most important reason we introduced traits is
that they make it easy to nail down which conditions have
failed on page load.

UIComponents
------------

The UIComponent class is the basic element we use to build our page models.
Anything that is part of a web page can be modelled as a UIComponent.
The responsibility of this class is to ensure lazy creation of a
WebElement.

In the example above, the InputText and Button classes extend UIComponent.

In general, a UIComponent may represent any portion of the DOM. It is
important to notice that a UIComponent can contain another UIComponent. An
example of this is the Table class.

Example
~~~~~~~

We want to build a model of the table at this address:
http://the-internet.herokuapp.com/challenging\_dom. We will build a
component class that allows interaction with the table. In particular,
we want to test that elements in the first row of the table match the
expected values. The complete example code can be found under the
`sample <https://github.com/Skyscanner/pages/tree/master/samples>`__
folder.

Again, we will build the test top-down.

.. code:: python

    EXPECTED_LABEL_LIST = ['Iuvaret0', 'Apeirian0', 'Adipisci0', 'Definiebas0', 'Consequuntur0', 'Phaedrum0', 'edit delete']

    class SampleTableTest(unittest.TestCase):

        def setUp(self):
            self.driver = WebDriver()

        def tearDown(self):
            self.driver.quit()

        def test_can_get_table_elements(self):
            sample_page = SamplePage(self.driver).load().wait_until_loaded()
            first_table_raw_values = sample_page.read_first_table_raw()

            assert_that(first_table_raw_values, equal_to(EXPECTED_LABEL_LIST))

SamplePage is a page object class which contains a table as a component.
We can start by writing the table. The Table class (available in
pages.standard\_components) makes this simple.

.. code:: python

    class SampleTable(Table):

        def __init__(self, driver):
            super(SampleTable, self).__init__(driver, 'sample table', [By.XPATH, './tbody/tr'], TableRow, 'raw',
                                              [By.XPATH, '//table'])

SampleTable extends Table which in turn extends UIComponent.
Moreover, when calling the super() method, we define TableRow as a
component representing a single row.

.. code:: python

    class TableRow(UIComponent):

        def __init__(self, driver, name):
            super(TableRow, self).__init__(driver, name)

        def values(self):
            return [i.text for i in self.locate().find_elements_by_xpath('./td')]

TableRow extends UIComponent and defines methods to access elements
in the row. The main problem has been split into smaller ones, and
we have written a very small amount of code.

Finally, we can define SamplePage.

.. code:: python

    class SamplePage(Page):

        def __init__(self, driver):
            Page.__init__(self, driver, 'sample page')
            self.add_trait(lambda: SampleTable(self.driver).is_present(), 'has table')

        def load(self):
            self.driver.get('http://the-internet.herokuapp.com/challenging_dom')
            return self

        def read_first_table_raw(self):
            table_raws = SampleTable(self.driver).get_items()
            return [i for i in table_raws[0].values()]

One thing to notice here is that the table object is created afresh
every time read\_first\_table\_raw() is called. While this makes sense
in most cases, as the content of the page may change dynamically after
loading (this is often the case for tables), in this case inspection of
the Table class tells us that calling \_\_init\_\_() does not result in
any WebDriver operation. The only moment when we locate elements on the
DOM is when we call get\_items().

This is the other key-concept of *pages*: by using UIComponent, we can
build components that instantiate a WebElement only when we need to use
it. This eliminates the possibility of StaleElementReferenceException(s)
to be raised during the execution.

Logging
=======

*pages* adds only a NullHandler to the loggers.
In order to turn on logging generated inside the library you can rely on root logger or set on explicitly.
To turn on logging from your application code, for instance:

.. code:: python

     logging.getLogger('pages').setLevel(logging.DEBUG)
     logging.basicConfig(level=logging.INFO)

This will set log level to DEBUG.


Distributing pages
==================

*pages* is distributed on PyPI.

Instructions
------------

-  Ensure .pypirc is present.
-  Update \_\_version\_\_ under pages/\_\_init\_\_.py.
-  Run *distribute.sh* under the *script* folder.

License
=======

*pages* is licensed under the Apache Software License 2.0 provision.

.. |BuildStatus| image:: https://travis-ci.org/Skyscanner/pages.svg
   :target: https://travis-ci.org/Skyscanner/pages
.. |CoverageStatus| image:: https://coveralls.io/repos/Skyscanner/pages/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/Skyscanner/pages?branch=master
.. |PyPI1| image:: https://img.shields.io/pypi/v/p-ages.svg
   :target: https://pypi.python.org/pypi/p-ages
.. |PyPI2| image:: https://img.shields.io/pypi/wheel/p-ages.svg
   :target: https://img.shields.io/pypi/wheel/p-ages.svg
.. |PyPI3| image:: https://img.shields.io/pypi/dm/p-ages.svg
   :target: https://pypi.python.org/pypi/p-ages
