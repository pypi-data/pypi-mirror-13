#coding:utf-8
from setuptools import setup, find_packages
setup(
      name="BiliCaptcha",
      version="0.0.4",
      description="Crack captcha when login on bilibili.com",
      author="buckle2000",
      author_email="buckle2000@163.com",
      url='example.com',
      license="LGPL",
      packages=find_packages(),
      install_requires = ['Pillow',],
)