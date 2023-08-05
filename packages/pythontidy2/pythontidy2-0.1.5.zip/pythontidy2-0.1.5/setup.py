from distutils.core import setup
long_description = '''
pythontidy2
===========

Usage
~~~~~

.. code:: python

    python -m pythontidy2 [-t expandtabsize] script.py

Installation
~~~~~~~~~~~~

.. code:: python

    pip install pythontidy2

Description
~~~~~~~~~~~

Tidy python scripts

Not compliant to PEP8

Effect
~~~~~~

From:

.. code:: python

    list = [1, 2, {
       'Alicedefg': '2341',
       'Beth' : "c",
       'Cecil' : '3258',
    }, 4]

To:

.. code:: python

    list = [1, 2, {
                    'Alicedefg' : '2341',
                    'Beth'      : "c",
                    'Cecil'     : '3258',
                    }, 4]

From:

.. code:: python

    doc = ""
    long_variable = ((doc+'\n') if doc else '')
    x = ""

To:

.. code:: python

    doc           = ""
    long_variable = ((doc + '\n') if doc else '')
    x             = ""

License
~~~~~~~

BSD
'''
setup(
  name = 'pythontidy2',
  packages = ['pythontidy2'], # this must be the same as the name above
  version = '0.1.5',
  description = 'Tidy Python Script',
  long_description=long_description,
  author = 'Boying Xu',
  author_email = 'xuboying@gmail.com',
  license='BSD',
  url = 'https://github.com/xuboying/pythontidy2', # use the URL to the github repo
  download_url = 'https://github.com/xuboying/pythontidy2/releases/tag/0.1.5', # I'll explain this in a second
  keywords = ['utility'], # arbitrary keywords
  classifiers = ['Programming Language :: Python :: 2', 'Programming Language :: Python :: 3'],
)