#coding:utf-8
from setuptools import setup
setup(
      name="BiliCaptcha",
      version="0.0.3",
      description="Crack captcha when login on bilibili.com",
      author="buckle2000",
      author_email="buckle2000@163.com",
      url='example.com',
      license="LGPL",
      py_modules=["bilicaptcha"],
      package_dir = {'bilicaptcha': '.'},
      #install_requires = ['Pillow',],
)