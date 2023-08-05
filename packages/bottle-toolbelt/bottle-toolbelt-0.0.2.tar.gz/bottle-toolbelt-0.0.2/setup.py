#from distutils.core import setup
from setuptools import setup, find_packages

# http://guide.python-distribute.org/quickstart.html
# python setup.py sdist
# python setup.py register
# python setup.py sdist upload
# pip install django-dynamic-fixture
# pip install django-dynamic-fixture --upgrade --no-deps
# Manual upload to PypI
# http://pypi.python.org/pypi/django-dynamic-fixture
# Go to 'edit' link
# Update version and save
# Go to 'files' link and upload the file

VERSION = '0.0.2'

tests_require = [
    'pytest==2.8.5',
    'tox==2.3.1',
]

install_requires = [
]

# from pip.req import parse_requirements
# install_requires = parse_requirements('requirements.txt')
# tests_require = parse_requirements('requirements-dev.txt')

setup(name='bottle-toolbelt',
      url='https://github.com/paulocheque/bottle-toolbelt',
      author="paulocheque",
      author_email='paulocheque@gmail.com',
      keywords='python bottle utility toolbelt',
      description='',
      license='MIT',
      classifiers=[
          'Operating System :: OS Independent',
          'Topic :: Software Development',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: Implementation :: PyPy',
      ],

      version=VERSION,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},

      packages=find_packages(),
)

