from itertools import imap
from setuptools import setup, find_packages
import pages


def get_requirements():
    reqs_file = "requirements/requirements.txt"
    try:
        with open(reqs_file) as reqs_file:
            reqs = filter(None, imap(lambda line: line.strip(), reqs_file))
            return reqs
    except IOError:
        pass
    return []

setup(
    name='p-ages',
    version=pages.__version__,
    author='valerio morsella',
    author_email='valerio.morsella@skyscanner.net',
    url='https://github.com/Skyscanner/pages',
    license='ASL v.2.0',
    packages=find_packages(exclude=["test*", "samples"]),
    description="pages is a lightweight page object and component Python library for UI tests",
    long_description=open('./README.rst').read(),
    install_requires=get_requirements(),
    test_suite="test",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "Programming Language :: Python :: 2.7",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Topic :: Software Development :: Testing"]
)
