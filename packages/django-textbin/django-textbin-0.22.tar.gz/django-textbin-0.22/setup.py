import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# py_version = sys.version_info[:2]
# if not py_version == (2, 7):
#     raise RuntimeError('Requires Python version 2.7 but '
#                        ' ({}.{} detected).'.format(*py_version))


setup(
    name='django-textbin',
    version='0.22',
    packages=['textbin', 'textbin.migrations'],
    url='https://github.com/zokalo/django-textbin',
    install_requires=[
        'django>=1.8.4',
        'djangorestframework>=3.3.2',
        'six>=1.5.2',
        'django-bootstrap3>=6.2.2',
        'django-recaptcha2>=0.1.7'
    ],
    include_package_data=True,  # use MANIFEST.in during install
    license='GPL v3.0',
    author='Don Dmitriy Sergeevich',
    author_email='dondmitriys@gmail.com',
    description='Django package for text sharing and exchanging',

    entry_points={
        'console_scripts': [
            'textbin = textbin.manage:main',
        ],
    },
)
