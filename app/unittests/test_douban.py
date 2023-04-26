import pytest
# from app.converter import douban

from ..converter import douban

t_scraper = 'requests'


def test_douban_note(scraper=t_scraper):
    url = 'https://www.douban.com/note/842596564'
    d = douban.Douban(url=url, scraper=scraper)
    return d.get_fav_item()


def test_douban_book_review(method=t_scraper):
    url = 'https://book.douban.com/review/11272483/'
    d = douban.Douban(url=url, scraper=method)
    return d.get_fav_item()


def test_douban_movie_review(method=t_scraper):
    url = 'https://movie.douban.com/review/15067446/'
    d = douban.Douban(url=url, scraper=method)
    return d.get_fav_item()


def test_douban_topic_post(method=t_scraper):
    url = 'https://www.douban.com/group/topic/287254123/'
    d = douban.Douban(url=url, scraper=method)
    return d.get_fav_item()


pytest