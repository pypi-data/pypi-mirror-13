'''
 # 说明：打包发布自己的模块.
 1、构建一个发布文件：命令python setup.py sdist（此时会在当前文件目录生成dist发布目录，里面有一个叫NestedRecursion-1.0.0.zip文件）
 2、将发布安装到本地的Python库里：命令python setup.py install
 3、安装完成后，import模块。若直接输入printMovieList(list)会报名，提示找不到。此时需要用命名空间解决。NestedRecursion.printMovieList(list)或 from NestedRecursion import printMovieList

 若需要发布到PyPI里共享代码，则需要注册PyPI账号。
 1、登录。python setup.py register  在命令行里输入注册的账号，并保存方便下次使用。
 2、上传发布。
 # 创建人：Tavis 
 # 创建时间：2015/12/26 12:21
'''
# coding=UTF-8


from distutils.core import setup

setup(
    # setup()函数的参数名
    name="NestedRecursion",
    version="1.0.0",
    py_modules=['NestedRecursion'],
    author="TavisD",
    author_email="tavisdxh@outlook.com",
    description="A simple printer of nested lists"
)
