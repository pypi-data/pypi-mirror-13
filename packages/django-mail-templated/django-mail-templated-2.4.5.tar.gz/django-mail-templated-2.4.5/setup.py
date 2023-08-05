import os
from setuptools import setup, find_packages


DESCRIPTION = 'Send emails using Django template system'

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.rst').read()
except:
    pass

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Framework :: Django',
]

VERSION = os.environ.get('MAIL_TEMPLATED_VERSION', '2.4.5')


setup(
    name='django-mail-templated',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    author='Artem Rizhov',
    author_email='artem.rizhov@gmail.com',
    url='https://github.com/artemrizhov/django-mail-templated',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
    test_suite='mail_templated.test_utils.run.run_tests',
)
