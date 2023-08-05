#从Python发布工具导入"setup"函数。
from distutils.core import setup

setup(
    #以下是setup函数的参数名
    name         = 'lintu_nester',
    version      = '1.3.0',
    py_modules   = ['nester'], #将模块的元数据与setup函数的参数关联。
    author       = 'hfpython',
    author_email = 'hfpython@headfirstlabs.com',
    url          = 'http://www.headfirstlabs.com',
    description  = 'A simple printer of nested lists',
    )
