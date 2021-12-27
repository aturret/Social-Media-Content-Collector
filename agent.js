Agent.receive = function () {
	var events = this.incomingEvents();
	var noTelegraph = RegExp(/(youtube\.com)|(bilibili\.com)|(t\.me)/);
	var simpreadHostExtract = RegExp(/^(?:[^:\n]+:\/\/)?([^:#/\n]*)/);
	var expre1 = JSON.stringify(Object.keys(events[0].payload.events[1])).replace(/\[\"/, "").replace(/\"\]/, ""); // switch needs same type
	var expre2 = JSON.stringify(Object.keys(events[0].payload.events[0])).replace(/\[\"/, "").replace(/\"\]/, "");

	if (Object.keys(events[0].payload.events[1]) == "telegraph") // If the first event is telegraph
	{
		switch (expre2) { //Checking for different huginn event. The default one is inoreader
			case "zhihu": {
				var zhihuAuthor = events[0].payload.events[0].zhihu.origin || "匿名用户";
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[1].telegraph.url + "\"><b>" + events[0].payload.events[0].zhihu.title + "</b></a>\nvia #Zhihu - <a href=\"" + events[0].payload.events[0].zhihu.originurl + "\">" + zhihuAuthor + "</a>\n<a href=\"" + events[0].payload.events[0].zhihu.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "weibo": {
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[1].telegraph.url + "\"><b>" + events[0].payload.events[0].weibo.title + "</b></a>\nvia #Weibo - <a href=\"" + events[0].payload.events[0].weibo.originurl + "\">" + events[0].payload.events[0].weibo.origin + "</a>\n<a href=\"" + events[0].payload.events[0].weibo.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "twitter": {
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[1].telegraph.url + "\"><b>" + events[0].payload.events[0].twitter.title + "</b></a>\nvia #Twitter - <a href=\"" + events[0].payload.events[0].twitter.originurl + "\">" + events[0].payload.events[0].twitter.origin + "</a>\n<a href=\"" + events[0].payload.events[0].twitter.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "blog": {
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[1].telegraph.url + "\"><b>" + events[0].payload.events[0].blog.title + "</b></a>\nvia #blog - <a href=\"" + events[0].payload.events[0].blog.originurl + "\">" + events[0].payload.events[0].blog.origin + "</a>\n<a href=\"" + events[0].payload.events[0].blog.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "douban": {
				var doubanMessage = events[0].payload.events[0].douban.comment || "";
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[1].telegraph.url + "\"><b>" + events[0].payload.events[0].douban.title + "</b></a>\nvia #Douban - <a href=\"" + events[0].payload.events[0].douban.originurl + "\">" + events[0].payload.events[0].douban.origin + "</a>\n" + doubanMessage + "\n<a href=\"" + events[0].payload.events[0].douban.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "simpread": {
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[1].telegraph.url + "\"><b>" + events[0].payload.events[0].simpread.title + "</b></a>\nvia #" + events[0].payload.events[0].simpread.category + " - <a href=\"" + simpreadHostExtract.exec(events[0].payload.events[0].simpread.originurl) + "\">" + events[0].payload.events[0].simpread.origin + "</a>\n<a href=\"" + events[0].payload.events[0].simpread.aurl + "\">阅读原文</a>"
				});
				break;
			}
			default: {
				if (noTelegraph.test(events[0].payload.events[0].inoreader.aurl)) {
					this.createEvent({
						"text": "<a href=\"" + events[0].payload.events[0].inoreader.aurl + "\"><b>" + events[0].payload.events[0].inoreader.title + "</b></a>\nvia #" + events[0].payload.events[0].inoreader.category + " - <a href=\"" + events[0].payload.events[0].inoreader.originurl + "\">" + events[0].payload.events[0].inoreader.origin + "</a>\n" + events[0].payload.events[0].inoreader.message + ""
					});
				} else {
					this.createEvent({
						"text": "<a href=\"" + events[0].payload.events[1].telegraph.url + "\"><b>" + events[0].payload.events[0].inoreader.title + "</b></a>\nvia #" + events[0].payload.events[0].inoreader.category + " - <a href=\"" + events[0].payload.events[0].inoreader.originurl + "\">" + events[0].payload.events[0].inoreader.origin + "</a>\n" + events[0].payload.events[0].inoreader.message + "\n<a href=\"" + events[0].payload.events[0].inoreader.aurl + "\">阅读原文</a>"
					});
				}
			}
		}

	} else
	{
		switch (expre1) {
			case "zhihu": {
				var zhihuAuthor = events[0].payload.events[1].zhihu.origin || "匿名用户";
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[0].telegraph.url + "\"><b>" + events[0].payload.events[1].zhihu.title + "</b></a>\nvia #Zhihu - <a href=\"" + events[0].payload.events[1].zhihu.originurl + "\">" + events[0].payload.events[1].zhihu.origin + "</a>\n<a href=\"" + events[0].payload.events[1].zhihu.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "weibo": {
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[0].telegraph.url + "\"><b>" + events[0].payload.events[1].weibo.title + "</b></a>\nvia #Weibo - <a href=\"" + events[0].payload.events[1].weibo.originurl + "\">" + events[0].payload.events[1].weibo.origin + "</a>\n<a href=\"" + events[0].payload.events[1].weibo.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "twitter": {
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[0].telegraph.url + "\"><b>" + events[0].payload.events[1].twitter.title + "</b></a>\nvia #Twitter - <a href=\"" + events[0].payload.events[1].twitter.originurl + "\">" + events[0].payload.events[1].twitter.origin + "</a>\n<a href=\"" + events[0].payload.events[1].twitter.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "blog": {
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[0].telegraph.url + "\"><b>" + events[0].payload.events[1].blog.title + "</b></a>\nvia #blog - <a href=\"" + events[0].payload.events[1].blog.originurl + "\">" + events[0].payload.events[1].blog.origin + "</a>\n<a href=\"" + events[0].payload.events[1].blog.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "douban": {
				var doubanMessage = events[0].payload.events[1].douban.comment || "";
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[0].telegraph.url + "\"><b>" + events[0].payload.events[1].douban.title + "</b></a>\nvia #Douban - <a href=\"" + events[0].payload.events[1].douban.originurl + "\">" + events[0].payload.events[1].douban.origin + "</a>\n" + doubanMessage + "\n<a href=\"" + events[0].payload.events[1].douban.aurl + "\">阅读原文</a>"
				});
				break;
			}
			case "simpread": {
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[0].telegraph.url + "\"><b>" + events[0].payload.events[1].simpread.title + "</b></a>\nvia #" + events[0].payload.events[1].simpread.category + " - <a href=\"" + simpreadHostExtract.exec(events[0].payload.events[1].simpread.originurl) + "\">" + events[0].payload.events[1].simpread.origin + "</a>\n<a href=\"" + events[0].payload.events[1].simpread.aurl + "\">阅读原文</a>"
				});
				break;
			}
			default: {
				if (noTelegraph.test(events[0].payload.events[1].inoreader.aurl)) {
					this.createEvent({
						"text": "<a href=\"" + events[0].payload.events[1].inoreader.aurl + "\"><b>" + events[0].payload.events[1].inoreader.title + "</b></a>\nvia #" + events[0].payload.events[1].inoreader.category + " - <a href=\"" + events[0].payload.events[1].inoreader.originurl + "\">" + events[0].payload.events[1].inoreader.origin + "</a>\n" + events[0].payload.events[1].inoreader.message + ""
					});
				} else {
					this.createEvent({
						"text": "<a href=\"" + events[0].payload.events[0].telegraph.url + "\"><b>" + events[0].payload.events[1].inoreader.title + "</b></a>\nvia #" + events[0].payload.events[1].inoreader.category + " - <a href=\"" + events[0].payload.events[1].inoreader.originurl + "\">" + events[0].payload.events[1].inoreader.origin + "</a>\n" + events[0].payload.events[1].inoreader.message + "\n<a href=\"" + events[0].payload.events[1].inoreader.aurl + "\">阅读原文</a>"

					});
				}
			}
		}
	}
}