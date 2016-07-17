# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import log
import MySQLdb
import MySQLdb.cursors
import logging
from twisted.enterprise import adbapi

class DoubanMoviePipeline(object):
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool(
                dbapiName ='MySQLdb',
                host ='127.0.0.1',
                db = 'moviedb',
                user = 'root',
                passwd = '',
                cursorclass = MySQLdb.cursors.DictCursor,
                charset = 'utf8',
                use_unicode = False
        )
 
    # pipeline dafault function
    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
        logging.debug(query)
        # print '+++++++++++++++++++++++++++++++++++++++++++++++++++++'
        return item
 
 
    # insert the data to databases
    def _conditional_insert(self, tx, item):
        # tx.execute("select * from doubanmovie where m_id= %s",(item['ID'],))
        # result=tx.fetchone()
        # log.msg(result,level=log.DEBUG)
        # print result
        # if result:
        #     log.msg("item already stored in db:%s" % item,level=log.DEBUG)
        # else:
            # types=role=writer=''
            # lentypes=len(item['types'])
            # lenrole=len(item['role'])
            # lenwriter=len(item['writer'])
            # for n in xrange(lentypes):
            #     types+=item['types'][n]
            #     if n<lentypes-1:
            #         types+='/'
            # for n in xrange(lenrole):
            #     types+=item['role'][n]
            #     if n<lenrole-1:
            #         role+='/'
            # for n in xrange(lenwriter):
            #     types+=item['writer'][n]
            #     if n<lenwriter-1:
            #         writer+='/'

        tx.execute("""
                insert into doubanmovie (m_url,m_id,m_name,m_director,m_writer,m_role,m_types,m_summary) values (%s,%s,%s,%s,%s,%s,%s,%s)
                """,(item['url'],item['ID'],item['name'],item['director'],item['writer'],item['role'],item['types'],item['summary']))
                # """,(item['url'],item['ID'][0],item['name'][0],item['director'][0],item['writer'][0],item['role'][0],item['types'][0],item['summary'][0]))
        log.msg("item stored success in db: %s" % item, level=log.DEBUG)

    def handle_error(self,e):
        log.err(e)
        # sql = "insert into pxtable(link) values('%s') " % parm
        # print '====================================================='
        #logging.debug(sql)
        # tx.execute(sql)
        # tx.commit()


