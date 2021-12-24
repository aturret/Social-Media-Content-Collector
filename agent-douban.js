Agent.receive = function () {
	var events = this.incomingEvents();
	// var doubanRegexp = RegExp(/(?<=(评语：))[^\\n]*/);

	if (Object.keys(events[0].payload.events[1]) == "telegraph") // If the first event is telegraph
	{
				var doubanMessage = doubanRegexp.exec(events[0].payload.events[0].douban.comment) || "";
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[1].telegraph.url + "\"><b>" + events[0].payload.events[0].douban.title + "</b></a>\nvia #Douban - <a href=\"" + events[0].payload.events[0].douban.originurl + "\">" + events[0].payload.events[0].douban.origin + "</a>\n" + doubanMessage + "\n<a href=\"" + events[0].payload.events[0].douban.aurl + "\">阅读原文</a>"
				});

	} else
	{
				var doubanMessage = doubanRegexp.exec(events[0].payload.events[1].douban.comment) || "";
				this.createEvent({
					"text": "<a href=\"" + events[0].payload.events[0].telegraph.url + "\"><b>" + events[0].payload.events[1].douban.title + "</b></a>\nvia #Douban - <a href=\"" + events[0].payload.events[1].douban.originurl + "\">" + events[0].payload.events[1].douban.origin + "</a>\n" + doubanMessage + "\n<a href=\"" + events[0].payload.events[1].douban.aurl + "\">阅读原文</a>"
				});
				
	}
}