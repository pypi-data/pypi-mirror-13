# -*- coding: utf-8 -*-
import io
from distutils.core import setup
with io.open('README', 'r', encoding='utf-8') as f:
    long_description = f.read()
f.close()

setup(
  name = 'pythontidy2',
  packages = ['pythontidy2'], # this must be the same as the name above
  version = '0.1.7',
  description = 'Tidy Python Script',
  long_description=long_description,
  author = 'Boying Xu',
  author_email = 'xuboying@gmail.com',
  license='BSD',
  url = 'https://github.com/xuboying/pythontidy2', # use the URL to the github repo
  download_url = 'https://github.com/xuboying/pythontidy2/releases/tag/0.1.7', # I'll explain this in a second
  keywords = ['utility'], # arbitrary keywords
  classifiers = ['Programming Language :: Python :: 2', 'Programming Language :: Python :: 3'],
)