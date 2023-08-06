# -*- coding: utf-8 -*-
import io
from distutils.core import setup
with io.open('README', 'r', encoding='utf-8') as f:
    long_description = f.read()
f.close()

ver = "0.1.9"

setup(
  name = 'pythontidy2',
  packages = ['pythontidy2'],
  version = ver,
  description = 'Tidy Python Script',
  long_description=long_description,
  author = 'Boying Xu',
  author_email = 'xuboying@gmail.com',
  license='BSD',
  url = 'https://github.com/xuboying/pythontidy2',
  download_url = 'https://github.com/xuboying/pythontidy2/releases/tag/%s' % ver,
  keywords = ['utility'],
  classifiers = ['Programming Language :: Python :: 2', 'Programming Language :: Python :: 3'],
)