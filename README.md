# Social-Media-Content-Collector

[中文版文档](https://github.com/aturret/Social-Media-Content-Collector/wiki/%E4%B8%AD%E6%96%87%E6%96%87%E6%A1%A3)

A simple API written in Flask. I originally wrote this program to make it easy to keep a copy of the social media information I see every day on [telegra.ph](https://telegra.ph) and forward it to [my telegram channel](https://t.me/aturretbillboard) into a form that can be easily read with telegram's instant view. As we all know, it is always difficult to keep the information in the Chinese world, so this is necessary for me.

Can be easily deployed on a server by Docker.

Demo site is not supported at this time.

The main difficulty of this project is how to crawl the information from each social media site, because the openness of each site and crawl rules vary. The rest is to go through the process of all kinds of boring API works.

The process of post HTML documents on telegra.ph uses  [html-telegraph-poster](https://github.com/mercuree/html-telegraph-poster) , which is much appreciated.

Currently supported social media:

- Weibo
- Twitter
- Zhihu
- Douban
- Inoreader RSS Broadcast Item

Please let me know if there is anything else you would like to support.

## Usage

### Deployment

After configuring the environment variables in the `.env` file in the same folder, deploy directly using the `docker-compose.yml` provided in the root directory or Docker program on your own server.

Docker-compose:

```bash
docker-compose up -d
```

Docker:

```bash
docker pull aturret/socialmediacollector
```

### Environment

  - TELEGRAM_BOT_KEY: The bound telegram bot token, not required if telegram forwarding is not used.
  - TWITTER_APP_KEY: Your twitter developer app key. It is required if you want to extract twitter content.
  - SITE_URL: set it to the domain name if you are binding to it. If not, it defaults to 127.0.0.1, the localhost.
  - CHANNEL_ID: If you want to do automatic forwarding, please fill in the corresponding telegram chat conversation id, and set your telegram bot as an admin of that chat.
  - PORT: the port number you provided, the default is 1045. if you want to change it to something else please change it together with the docker deployment.

## API Document

