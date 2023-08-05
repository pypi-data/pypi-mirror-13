scrapy_qiniu
=====

适用于Scrapy的Pipeline插件。扩展了Scrapy自带的FilesPipeline，可以将静态资源上传到七牛云
存储上面。

* 支持缓存，可以避免静态资源的重复下载
* 采用fetch模式，让七牛服务器代为下载，而不用像默认的FilesPipeline那样，先下载到爬虫所在
  主机，然后再上传到七牛服务器


