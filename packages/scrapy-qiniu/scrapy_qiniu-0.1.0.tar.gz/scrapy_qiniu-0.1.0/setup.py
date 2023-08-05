# -*- coding: utf-8 -*-
from setuptools import setup
LONGDOC = """
scrapy_qiniu
=====

适用于Scrapy的Pipeline插件。扩展了Scrapy自带的FilesPipeline，可以将静态资源上传到七牛云
存储上面。

* 支持缓存，可以避免静态资源的重复下载
* 采用fetch模式，让七牛服务器代为下载，而不用像默认的FilesPipeline那样，先下载到爬虫所在
  主机，然后再上传到七牛服务器
"""

setup(name='scrapy_qiniu',
      version='0.1.0',
      description='Scrapy pipeline extension for qiniu.com',
      long_description=LONGDOC,
      author='Zephyre',
      author_email='haizi.zh@gmail.com',
      url='https://github.com/haizi-zh/scrapy-qiniu',
      license="MIT",
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Framework :: Scrapy',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Console',
      ],
      keywords='crawler,spider,scrapy,qiniu',
      packages=['scrapy_qiniu'],
      install_requires=['Scrapy', 'qiniu'],
)
