#coding=utf-8

import re
import time
from scrapy.selector import Selector
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor as le
from douban_movie.items import DoubanMovieItem

class moviespider(CrawlSpider):
    name="doubanmovie"
    allowed_domains=["movie.douban.com"]
    start_urls=["http://movie.douban.com"]
    rules=[
        # Rule(le(allow=('movie.douban.com/subject/\d+/.+',)),follow=True),
        Rule(le(allow=('movie.douban.com/subject/(\d+)/(?:\?from|$)', )),callback='parse_item',follow=True),
        # Rule(le(allow=('movie.douban.com/subject/\d{8}/$', )),callback='parse_item',follow=True),
        # Rule(le(allow=(r'http://movie.douban.com/subject/\d+/.*')),callback="parse_item"),
    ]
    def __init__(self):
        CrawlSpider.__init__(self)
        self.count = 0
        self.MAX_MOVIE = 2000

    def parse_item(self,response):
        # hxs=HtmlXPathSelector(response)
        # sel=Selector(response)
        item=DoubanMovieItem()
        # items.py定义的内容
        # url=Field()
        # ID=Field()
        # name=Field()
        # director=Field()
        # writer=Field()
        # role=Field()
        # types=Field()
        # summary=Field()
        item['url']=re.match(string=''.join(response.url), pattern='(https://movie.douban.com/subject/\d+)/.*').group(1)
        item['movieid'] = item['url'].split('/')[-1]
        item['ID']='/'.join(response.xpath('//*/a[contains(@href,"subject")]/@href').re('movie.douban.com/subject/(\d+)/(?:\?from|$)'))
        # item['ID']=''.join(response.xpath('//*[@id="content"]/div/div[1]/div[1]/div[3]/ul/li[5]/span/@id').extract())
        item['name']=''.join(response.xpath('//*[@id="content"]/h1/span[1]/text()').extract())
        item['director']='/'.join(response.xpath('//*[@id="info"]/span[1]/span[2]/a/text()').extract())
        item['writer']='/'.join(response.xpath('//*[@id="info"]/span[2]/span[2]/a/text()').extract())
        item['role']='/'.join(response.xpath('//*[@id="info"]/span[3]/span[2]/a/text()').extract())
        item['types']='/'.join(response.xpath('//span[@property="v:genre"]/text()').extract())
        item['summary']=''.join(response.xpath('//span[@property="v:summary"]/text()').extract())
        item['summary'] = item['summary'].strip().\
            replace('<br />', '').replace('\t', ' ').\
            replace('\n', ' ').replace('&amp', '').replace('&quot;','').replace(u'\u3000', '')
        item['summary'] = re.sub(r' {1,}', ' ', item['summary'])
        if self.count == self.MAX_MOVIE:
            while True:
                print 'You have got {0} movies, please quit!'.format(self.MAX_MOVIE)
                time.sleep(2)
        self.count += 1
        yield item
        # return item
