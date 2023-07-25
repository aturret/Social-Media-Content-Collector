# 社交媒体收集器

用Flask写的一个简单的API。最初写这个程序的目的是，方便我把日常看到的社交媒体信息在[telegra.ph](https://telegra.ph)上留存一份，转发到[我的telegram channel](https://t.me/aturretbillboard)上，变成可以方便使用telegram的instant view阅读的形式。众所周知，简体中文世界的信息总是很难得以长久保全，这样的做法非常有必要。

支持Docker一键部署。

财力有限，暂不支持提供演示网站。

主要难点在于如何爬取各个社交媒体网站的信息，因为各个网站的开放性和爬取规则各不相同。剩下的都是走流程的各类API搬砖。

把HTML文档提交到telegra.ph的过程采用了GitHub上的开源项目[html-telegraph-poster](https://github.com/mercuree/html-telegraph-poster)，非常感谢。

目前支持的社交媒体有：

- 微博
- Twitter
- 知乎
- 豆瓣
- Inoreader的RSS转发信息

  如果还有什么希望能提供支持的，请告诉我。


## 使用

### Docker部署

在同文件夹下的`.env`文件中配置好环境变量后，直接使用根目录下提供的`docker-compose.yml`或者docker程序进行部署。

Docker-compose:

```bash
docker-compose up -d
```

Docker:

```bash
docker pull aturret/socialmediacollector
```

### 环境变量配置项说明

```
- TELEGRAM_BOT_KEY: 绑定的telegram bot token。如果不使用telegram转发功能则不需要。
- TWITTER_APP_KEY: 你的twitter开发者key。如果要摘取twitter内容则必须要。
- SITE_URL: 站点url。如果绑定域名请填写，不填写则默认是localhost127.0.0.1。
- CHANNEL_ID: 如果要进行自动转发，则请填写对应的telegram聊天对话id，并将你的telegrambot设定为该聊天的管理员。
- PORT: 你所提供的端口号，默认是1045。如果要改成别的请在docker部署时一并修改。
```

## API简单说明

摘取内容后，所有API的返回值都是一个字典，其内容为：

```python
mdict = {
    		   'category':'',		#分类
                'title': '',		#标题
                'author': '',		#出处
    		   'aurl': '',		#作者链接
                'author_url': '',	#原文链接
    		   'message':'',        #转发时附带的评论
                't_url': ''			#
            }
```

