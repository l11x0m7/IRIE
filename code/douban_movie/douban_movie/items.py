# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item,Field


class DoubanMovieItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url=Field()
    movieid=Field()
    ID=Field()
    name=Field()
    director=Field()
    writer=Field()
    role=Field()
    types=Field()
    summary=Field()


