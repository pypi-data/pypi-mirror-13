# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

VERSION = __import__("delay").__version__
LONGDOC = """

A python Function / Method delay executing system base on function Decorators.

Auto delay the Function execution for a certain period time.
The new function will replace the older one and reset the countdown of the delay time.

GitHub: https://github.com/bazookapb/delay_decorator.git

特点

- 兼容各种版本的python，包括python2和python3的个版本；
- 使用方便：一个装饰器放到方法的头部即可延时执行该方法；
- MIT 授权协议；


安装说明

代码对 Python 2/3 均兼容

1. 全自动安装： ``easy_install delay_decorator`` 或者 ``pip install delay_decorator`` / ``pip3 install delay_decorator``
2. 半自动安装：先下载 https://pypi.python.org/pypi/wrapcache/ ，解压后运行
   python setup.py install
3. 手动安装：将 delay_decorator 目录放置于当前目录或者 site-packages 目录

通过 import delay_decorator 来引用

"""

setup(name = 'delay_decorator',
      version = '1.0.1',
      description = 'A python Function / Method delay executing system base on function Decorators.',
      long_description = LONGDOC,
      author = 'pangbo',
      author_email = 'pangbo@gmail.com',
      url = 'https://github.com/hustcc/wrapcache',
      license = "MIT",
      classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        "Programming Language :: Python",
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        'Topic :: Software Development :: Embedded Systems'
      ],
      keywords='delay, decorator, python, schedule',
      packages=find_packages(),
      zip_safe=False,
)
