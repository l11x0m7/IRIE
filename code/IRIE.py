#!/usr/bin/env python
# coding=utf-8

import os
import time
import sys
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import urllib
import urllib2
import json
import re
import numpy as np
reload(sys)
sys.setdefaultencoding('utf-8')

# HTML的URL解析
class MyHtmlParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.url_list = []
	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			# print "Start tag:", tag
			for attr in attrs:
				if attr[0] == 'href' and attr[1].\
				startswith('https://movie.douban.com/subject/'):
					self.url_list.append(attr[1])

	# def handle_endtag(self, tag):
	#     print "End tag  :", tag

	# def handle_data(self, data):
	#     print "Data     :", data

	# def handle_comment(self, data):
	#     print "Comment  :", data

	# def handle_entityref(self, name):
	#     c = unichr(name2codepoint[name])
	#     print "Named ent:", c

	# def handle_charref(self, name):
	#     if name.startswith('x'):
	#         c = unichr(int(name[1:], 16))
	#     else:
	#         c = unichr(int(name))
	#     print "Num ent  :", c

	# def handle_decl(self, data):
	#     print "Decl     :", data

# 电影搜索引擎
class MovieSE:
	def __init__(self):
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
		self.headers = { 'User-Agent' : user_agent }
		self.mhp = MyHtmlParser()
		self.moviehead = 'https://movie.douban.com/subject/'

	# 下载html文档
	def HtmlDownloader(self, origin_url, file_number, html_dir='../data/html/'):
		if not os.path.exists(html_dir):
			os.mkdir(html_dir)
		req = urllib2.Request(origin_url, headers=self.headers)
		res = urllib2.urlopen(req)
		content = res.read().decode()
		self.mhp.feed(content)
		pattern = r'.*?movie.douban.com/subject/(\d+)/(?:\?from|$)'
		origin_url_list = list()

		for url in self.mhp.url_list:
			res = re.match(pattern, url)
			if res != None:
				origin_url_list.append(res.group(1))
		time.sleep(1)

		movie_reflect = dict()
		count = 0
		useless_url = set()
		while len(origin_url_list) != 0:
			sec_url_list = list()
			for o_url in origin_url_list:
				if o_url in movie_reflect or o_url in useless_url:
					continue
				try:
					req = urllib2.Request(self.moviehead + o_url, \
						headers=self.headers)
					res = urllib2.urlopen(req)
					content = res.read().decode()
				except:
					useless_url.add(o_url)
					print '[Error]: {0}'.format(o_url)
				else:
					with open(html_dir + '{0}.html'.format(o_url), 'w') as fw:
						fw.write(content.encode('utf-8'))
					count += 1
					movie_reflect[o_url] = dict()
					
					print 'ID:{2}.You have got {0} html file(s), {1} in total.'\
					.format(count, file_number, o_url)
					if count >= file_number:
						with open('../data/pagerank.json', 'w') as fw:
							fw.write(json.dumps(movie_reflect)+'\n')
						return 'Finished!'
					self.mhp.feed(content)
					for url in self.mhp.url_list:
						res = re.match(pattern, url)
						if res != None:
							sec_url_list.append(res.group(1))
							movie_reflect[o_url].setdefault(res.group(1), 0)
							movie_reflect[o_url][res.group(1)] += 1
				time.sleep(1)

			origin_url_list = sec_url_list
			time.sleep(1)

		print 'Return back before getting {0} html files!'.format(file_number)
		with open('../data/pagerank.json', 'w') as fw:
			fw.write(json.dumps(movie_reflect)+'\n')
		return 'Not finished!'

	# 解析html文档里的电影信息
	# 电影信息（电影名称、导演、编剧、主演、类型、简介）
	def HtmlParser(self, html_dir='../data/html', raw_info='../data/info'):
		if not os.path.exists(raw_info):
			os.mkdir(raw_info)
		dir_files = os.listdir(html_dir)
		pattern = r'<div id="info">(.*?)</div>'
		pattern_name = u"""<a name="intro">.*?<h2>(.*?)的剧情简介"""
		pattern_director = r'"v:directedBy">(.*?)</a>'
		pattern_writer = u"""<span ><span class='pl'>编剧</span>(.*?)</span>"""
		pattern_writer_name = r'">(.*?)</a>'
		pattern_actor = r'"v:starring">(.*?)</a>'
		pattern_type = r'"v:genre">(.*?)</span>'
		pattern_summary = r'"v:summary".*?>(.*?)</span>'
		for filename in dir_files:
			# movie_info = {'name':'', 'director':[], 'writer':[], 'actor':[]\
			# 'type':[], summary:''}
			print 'Current file id: {0}'.format(filename)
			movie_info = dict()
			with open(html_dir + '/' + filename) as fr:
				content = '\n'.join(fr.readlines()).decode()
				res = re.findall(pattern, content, re.S)[0]
				# print res
				name = re.findall(pattern_name, content, re.S)
				if len(name) > 0:
					movie_info['name'] = name[0].strip()
				else:
					movie_info['name'] = ''

				movie_info['director'] = re.findall(pattern_director, res, re.S)
				writer = re.findall(pattern_writer, res, re.S)
				if len(writer) > 0:
					movie_info['writer'] = re.findall(pattern_writer_name, writer[0], re.S)
				else:
					movie_info['writer'] = []
				movie_info['actor'] = re.findall(pattern_actor, res, re.S)
				movie_info['type'] = re.findall(pattern_type, res, re.S)
				summary = re.findall(pattern_summary, content, re.S)
				if len(summary) > 0:
					movie_info['summary'] = summary[0].strip().\
						replace('<br />', '').replace('\t', ' ').\
						replace('\n', ' ').replace('&amp', '').replace(u'\u3000', '')
					movie_info['summary'] = re.sub(r' {1,}', ' ', movie_info['summary'])
				else:
					movie_info['summary'] = ''
				movie_id = filename.split('.')[0]
				movie_info['url'] = self.moviehead + movie_id
				# print json.dumps(movie_info, ensure_ascii=False)
				with open(raw_info + '/' + movie_id + '.json', 'w') as fw:
					fw.write(json.dumps(movie_info).encode('utf-8') + '\n')

	# 做初始网页排名
	def PageRank(self):
		pass

	# 扩展分词词典，加大分词准确率
	def ExpandDict(self, raw_info='../data/info'):
		from jieba import add_word
		from jieba import cut_for_search
		self.cutter = cut_for_search
		if not os.path.exists(raw_info):
			return '[Error]: file or directory "{0}" doesn\'t exist.'.format(raw_info)
		file_list = os.listdir(raw_info)
		for filename in file_list:
			with open(raw_info + '/' + filename) as fr:
				movie_info = json.loads(fr.readlines()[0].strip())
				add_word(movie_info['name'])
				if ' ' in movie_info['name']:
					for word in movie_info['name'].split(' '):
						# print word
						add_word(word)
				if u'：' in movie_info['name']:
					for word in movie_info['name'].split(u'：'):
						add_word(word)
				if u':' in movie_info['name']:
					for word in movie_info['name'].split(u':'):
						add_word(word)
				for word in movie_info['director']:
					# print word
					add_word(word)
				for word in movie_info['writer']:
					# print word
					add_word(word)
				for word in movie_info['actor']:
					# print word
					add_word(word)
		return '[Info]: WS Dictionary Loading Success!'

	# 加载停用词/功能词
	def LoadStopwords(self):
		stop_words = set()
		with open(u'../dict/stopwords/file/中文停用词库.txt') as fr:
			for line in fr:
				item = line.strip().decode()
				stop_words.add(item)
		with open(u'../dict/stopwords/file/哈工大停用词表.txt') as fr:
			for line in fr:
				item = line.strip().decode()
				stop_words.add(item)
		with open(u'../dict/stopwords/file/四川大学机器智能实验室停用词库.txt') as fr:
			for line in fr:
				item = line.strip().decode()
				stop_words.add(item)
		with open(u'../dict/stopwords/file/百度停用词列表.txt') as fr:
			for line in fr:
				item = line.strip().decode()
				stop_words.add(item)
		with open(u'../dict/stopwords/file/stopwords_net.txt') as fr:
			for line in fr:
				item = line.strip().decode()
				stop_words.add(item)
		with open(u'../dict/stopwords/file/stopwords_net2.txt') as fr:
			for line in fr:
				item = line.strip().decode()
				stop_words.add(item)
		print '[Info]: Stopwords Dictionary Loading Success!'
		return stop_words

	# 建立索引
	def IndexBuilder(self, raw_info='../data/info', index = '../data/index'):
		if not os.path.exists(raw_info):
			return
		if not os.path.exists(index):
			os.mkdir(index)
		if not os.path.exists(index + '/' + 'dtmat.json') or \
			not os.path.exists(index + '/' + 'keyword.json') or \
			not os.path.exists(index + '/' + 'movieid.json'):
			ret = self.ExpandDict(raw_info)
			print ret
			if ret.startswith('[Error]'):
				return
			stop_words = self.LoadStopwords()
			raw_info_list = os.listdir(raw_info)
			doc_num = len(raw_info_list)
			movie_list = list()
			doc_words = dict()
			for movie_info in raw_info_list:
				with open(raw_info + '/' + movie_info) as fr:
					details = json.loads(fr.readlines()[0].strip())
					word_list = list()
					# word_list.append(details['name'])
					word_list.extend(list(self.cutter(details['name'])))
					# word_list.extend(details['director'])
					for word in details['director']:
						word_list.extend(list(self.cutter(word)))
					# word_list.extend(details['writer'])
					for word in details['writer']:
						word_list.extend(list(self.cutter(word)))
					# word_list.extend(details['actor'])
					for word in details['actor']:
						word_list.extend(list(self.cutter(word)))
					word_list.extend(details['type'])
					word_list.extend(list(self.cutter(details['summary'])))
					movie_id = movie_info.split('.')[0]
					movie_list.append(movie_id)
					doc_words[movie_id] = word_list
			word_docfreq = dict()
			for docname, words in doc_words.iteritems():
				for word in words:
					if word in stop_words:
						continue
					word_docfreq.setdefault(word, dict())
					if not word_docfreq[word].has_key(docname):
						word_docfreq[word][docname] = words.count(word)

			keyword_list = list()
			for word in word_docfreq:
				docfreq = word_docfreq[word]
				doc, freq = zip(*(docfreq.items()))
				tf_idf = float('-inf')
				for i, f in enumerate(freq):
					tf = float(f)/len(doc_words[doc[i]])
					idf = np.log2(float(doc_num)/(len(doc)+1))
					tf_idf = max(tf * idf, tf_idf)
				if tf_idf >= 0.1:
					keyword_list.append(word)

			dt_mat = np.zeros((len(keyword_list), len(movie_list)))
			for i, word in enumerate(keyword_list):
				for j, movie_id in enumerate(movie_list):
					dt_mat[i,j] = word_docfreq[word].get(movie_id, 0)
			print '[Info]: Index Building Success! You\'ve got {0} indeces and {1} movies'.\
				format(len(keyword_list), len(movie_list))
			# with open(index + '/' + 'dtmat.json', 'w') as fw:
			# 	fw.write(json.dumps(dt_mat.tolist()))
			# with open(index + '/' + 'keyword.json', 'w') as fw:
			# 	fw.write(json.dumps(keyword_list))
			# with open(index + '/' + 'movieid.json', 'w') as fw:
			# 	fw.write(json.dumps(movie_list))
		else:
			with open(index + '/' + 'dtmat.json') as fr:
				dt_mat = np.array(json.loads(fr.readlines()[0].strip()))
			with open(index + '/' + 'keyword.json') as fr:
				keyword_list = np.array(json.loads(fr.readlines()[0].strip()))				
			with open(index + '/' + 'movieid.json') as fr:
				movie_list = np.array(json.loads(fr.readlines()[0].strip()))
			print '[Info]: Index Load Success!'
		return dt_mat, keyword_list, movie_list


		# print json.dumps(doc_words['26775951'], ensure_ascii=False)

	# 隐含语义索引
	def LSI(self, raw_info, index):
		from numpy import linalg
		import pickle
		dt_mat, keyword_list, movie_list = self.IndexBuilder(raw_info, index)
		if not os.path.exists('dtmat.pkl'):
			u, s, v = linalg.svd(dt_mat)
			new_len = int(0.5*len(s))
			tmp_s = s[0:new_len]
			new_u = u[:,:new_len]
			new_v = v[:new_len,:]
			new_s = np.zeros((new_len, new_len))
			for i in range(new_len):
				new_s[i,i] = tmp_s[i]
			new_dt_mat = new_u.dot(new_s).dot(new_v)

			dt_pickle = open('dtmat.pkl', 'wb')
			pickle.dump(new_dt_mat, dt_pickle)
			dt_pickle.close()
		else:
			dt_pickle = open('dtmat.pkl', 'rb')
			new_dt_mat = pickle.load(dt_pickle)
		print '[Info]: Load LSI Matrix Success!'
		return new_dt_mat, keyword_list, movie_list


	# 语句查询
	def Query(self, query, raw_info, index, LSI=False):
		if LSI:
			dt_mat, keyword_list, movie_list = \
				self.LSI(raw_info, index)
		else:
			dt_mat, keyword_list, movie_list = \
				self.IndexBuilder(raw_info, index)

		query_list = list(self.cutter(query))
		if query not in query_list:
			query_list.append(query)
		query_vec = np.zeros((1, len(keyword_list)))
		for i, keyword in enumerate(keyword_list):
			query_vec[0,i] = query_list.count(keyword)
			if keyword == query:
				query_vec[0,i] *= 10
		relation_vec = query_vec.dot(dt_mat)
		ind_vec = list(reversed(np.argsort(relation_vec.tolist())[0]))

		count = 0
		for i in range(min(len(ind_vec), 50)):
			movie_id = movie_list[ind_vec[i]]
			if relation_vec[0,ind_vec[i]] <= 0:
				break
			count += 1
			with open(raw_info + '/' + movie_id + '.json') as fr:
				movie_info = json.loads(fr.readlines()[0].strip())
				print '索引排名:', i+1
				print '电影ID:', movie_id
				print '电影名称:', movie_info['name']
				print '导演:', ','.join(movie_info['director'])
				print '编剧:', ','.join(movie_info['writer'])
				print '主演:', ','.join(movie_info['actor'])
				print '类型:', ','.join(movie_info['type'])
				print '简介:', movie_info['summary']
				print '网址:', movie_info['url']
				print
		print '以上即为查询结果，共{0}条。'.format(count)




if __name__ == '__main__':
	mse = MovieSE()
	# ret_info = mse.HtmlDownloader('https://movie.douban.com/', 5000)
	# print ret_info
	# mse.HtmlParser('../data/html', '../data/info')
	# mse.IndexBuilder('../data/info_bak', '../data/index_bak')
	# mse.LSI('../data/info_bak', '../data/index_bak')
	mse.Query('惊天魔盗团', '../data/info', '../data/index', LSI=False)
	# mse.Query(u'开心')