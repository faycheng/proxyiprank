from __future__ import division
import urllib2
import time
import random
import math
import json
import logging
import threading
import traceback
from cStringIO import StringIO
from operator import itemgetter
from multiprocessing.dummy import Pool as ThreadPool
from lxml import etree
from proxyiprank import ProxyIPRank
import gzip
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')

proxyip_set = set()
logging.basicConfig(filename='proxyip_spider.log', level=logging.INFO, format='%(asctime)s %(levelname)s \n\t\t%(message)s', datefmt='%Y.%m.%d  %H:%M:%S')
logging.info('Start crawling proxyips:')

user_agents = [
		('User-agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'),
		('User-agent','Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36'),
		('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.2 (KHTML, like Gecko) ChromePlus/4.0.222.3 Chrome/4.0.222.3 Safari/532.2'),
		('User-agent','Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'),
		('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20130401 Firefox/31.0'),
		('User-agent','Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201'),
		('User-agent','Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/533.1 (KHTML, like Gecko) Maxthon/3.0.8.2 Safari/533.1'),
		('User-agent','Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; Maxthon/3.0)'),
		('User-agent','Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16'),
		('User-agent','Opera/9.80 (Windows NT 6.1; WOW64; U; pt) Presto/2.10.229 Version/11.62'),
		('User-agent','Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36'),
		('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/527+ (KHTML, like Gecko) QtWeb Internet Browser/3.0 http://www.QtWeb.net'),
		('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; pt-BR) AppleWebKit/533.3 (KHTML, like Gecko) QtWeb Internet Browser/3.7 http://www.QtWeb.net'),
		('User-agent','Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36'),
		('User-agent','Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:27.0) Gecko/20121011 Firefox/27.0')
	]

target_urls = [
		{'http://www.kuaidaili.com/free/outha/':43200},
		{'http://www.kuaidaili.com/free/inha/':43200},
		{'http://cn-proxy.com/':10800},
		{'http://www.haodailiip.com/':3600},
		{'http://www.66ip.cn/index.html':43200},
		{'http://ip.izmoney.com/search/china/high/index.html':1800},
		{'http://proxy.mimvp.com/free.php?proxy=in_hp&sort=&pageindex=1':1800},
		{'http://proxy.mimvp.com/free.php?proxy=out_hp':1800}
	]

def request_url(target_url):
	try:
		proxyip = '115.159.5.247:80'
		proxy_handler = urllib2.ProxyHandler({'http':proxyip})
		proxy_opener = urllib2.build_opener(proxy_handler)
		urllib2.install_opener(proxy_opener)
		req = urllib2.Request(target_url)
		user_agent_index = random.randint(0, 12)
		req.add_header(user_agents[user_agent_index][0], user_agents[user_agent_index][1])
		req.add_header('Accept-encoding', 'gzip')
		start_time = time.time()
		content = urllib2.urlopen(req, timeout = 10).read()
		end_time = time.time()
		check_time =  end_time - start_time
		print 'Cawled %s.\nUsing time:%f'%(target_url ,check_time)
		logging.info('Cawled %s.\nUsing time:%f'%(target_url ,check_time))
		return content
	except Exception, e:
		logging.info('Cawled %s failed.'%target_url)
		logging.exception(e)

def request_one():
	while 1:
		try:
			target_url = 'http://www.kuaidaili.com/free/outha/'
			sleep_time = 43200
			content_gzip = request_url(target_url)
			content_str = gzip.GzipFile(fileobj=StringIO(content_gzip), mode="r")
			content_str = content_str.read().decode('utf-8').encode('utf-8')
			content_str = content_str.decode('utf-8', 'ignore')
			content_buf = StringIO(unicode(content_str))
			parser = etree.HTMLParser()
			content_tree = etree.parse(content_buf, parser = parser)
			basic_xpath_str = '/html/body/div[2]/div/div[2]/table/tbody/tr[{arg_tr_index}]/td[{arg_td_index}]/text()'
			for tr_index in range(1, 16):
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 1)
				proxyip = content_tree.xpath(xpath_str)
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 2)
				proxyport = content_tree.xpath(xpath_str)
				proxyip_set.add(proxyip[0] + ':' + proxyport[0])
		except Exception, e:
			logging.exception(e)
		finally:
			time.sleep(sleep_time)


def request_two():
	while 1:
		try:
			target_url = 'http://www.kuaidaili.com/free/inha/'
			sleep_time = 43200
			content_gzip = request_url(target_url)
			content_str = gzip.GzipFile(fileobj=StringIO(content_gzip), mode="r")
			content_str = content_str.read().decode('utf-8').encode('utf-8')
			content_str = content_str.decode('utf-8', 'ignore')
			content_buf = StringIO(unicode(content_str))
			parser = etree.HTMLParser()
			content_tree = etree.parse(content_buf, parser = parser)
			basic_xpath_str = '/html/body/div[2]/div/div[2]/table/tbody/tr[{arg_tr_index}]/td[{arg_td_index}]/text()'
			for tr_index in range(1, 16):
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 1)
				proxyip = content_tree.xpath(xpath_str)
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 2)
				proxyport = content_tree.xpath(xpath_str)
				proxyip_set.add(proxyip[0] + ':' + proxyport[0])
		except Exception, e:
			logging.exception(e)
		finally:
			time.sleep(sleep_time)
def request_three():
	while 1:
		try:
			target_url = 'http://cn-proxy.com/'
			sleep_time = 10800
			content_gzip = request_url(target_url)
			content_str = gzip.GzipFile(fileobj=StringIO(content_gzip), mode="r")
			content_str = content_str.read().decode('utf-8').encode('utf-8')
			content_str = content_str.decode('utf-8', 'ignore')
			content_buf = StringIO(unicode(content_str))
			parser = etree.HTMLParser()
			content_tree = etree.parse(content_buf, parser = parser)
			basic_xpath_str = '/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div[2]/table/tbody/tr[{arg_tr_index}]/td[{arg_td_index}]/text()'
			for tr_index in range(1, 36):
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 1)
				proxyip = content_tree.xpath(xpath_str)
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 2)
				proxyport = content_tree.xpath(xpath_str)
				proxyip_set.add(proxyip[0] + ':' + proxyport[0])
			basic_xpath_str = '/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div[4]/table/tbody/tr[{arg_tr_index}]/td[{arg_td_index}]/text()'
			for tr_index in range(1, 36):
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 1)
				proxyip = content_tree.xpath(xpath_str)
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 2)
				proxyport = content_tree.xpath(xpath_str)
				proxyip_set.add(proxyip[0] + ':' + proxyport[0])
		except Exception, e:
			logging.exception(e)
		finally:
			time.sleep(sleep_time)

def request_four():
	while 1:
		try:
			target_url = 'http://www.haodailiip.com/'
			sleep_time = 3600
			content_gzip = request_url(target_url)
			content_str = gzip.GzipFile(fileobj=StringIO(content_gzip), mode="r")
			content_str = content_str.read().decode('utf-8').encode('utf-8')
			content_str = content_str.decode('utf-8', 'ignore')
			content_buf = StringIO(unicode(content_str))
			parser = etree.HTMLParser()
			content_tree = etree.parse(content_buf, parser = parser)
			xpath_str = "//tr[@style='font-size: 16px;background-color:#F8F8FF;  line-height: 30px;']/td[1]"
			proxyip_list = content_tree.xpath(xpath_str)
			xpath_str = "//tr[@style='font-size: 16px;background-color:#F8F8FF;  line-height: 30px;']/td[2]"
			proxyport_list = content_tree.xpath(xpath_str)
			for x in range(len(proxyip_list)):
				proxyip_set.add(str(proxyip_list[x].text).strip() + ':' + str(proxyport_list[x].text).strip()) 
			xpath_str = "//tr[@style='font-size: 16px;line-height: 30px;']/td[1]"
			proxyip_list = content_tree.xpath(xpath_str)
			xpath_str = "//tr[@style='font-size: 16px;line-height: 30px;']/td[2]"
			proxyport_list = content_tree.xpath(xpath_str)
			for x in range(len(proxyip_list)):
				proxyip_set.add(str(proxyip_list[x].text).strip() + ':' + str(proxyport_list[x].text).strip()) 
		except Exception, e:
			logging.exception(e)
		finally:
			time.sleep(sleep_time)
		
# def request_five():
# 	while 1:
# 		target_url = 'http://proxy.goubanjia.com/'
# 		sleep_time = 43200
# 		print 'Cawling ', target_url
# 		content_gzip = request_url(target_url)
# 		content_str = gzip.GzipFile(fileobj=StringIO(content_gzip), mode="r")
# 		content_str = content_str.read().decode('utf-8').encode('utf-8')
# 		content_str = content_str.decode('utf-8', 'ignore')
# 		content_buf = StringIO(unicode(content_str))
# 		parser = etree.HTMLParser()
# 		with open('tmp.html', 'a+') as fd:
# 			fd.write(content_str)
# 		content_tree = etree.parse(content_buf, parser = parser)
# 		basic_xpath_str = '/html/body/div[4]/div[1]/div/div[3]/div[2]/table/tbody/tr[{arg_tr_index}]/td[{arg_td_index}]'
# 		for tr_index in range(1, 21):
# 			xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 1)
# 			proxyip_node = content_tree.xpath(xpath_str + '/*')
# 			proxyip_str = ''
# 			for child_element in proxyip_node:
# 				print child_element.text, child_element.attrib, child_element.tag
# 				if str(child_element.attrib).find('none') == -1:
# 					print '########' , child_element.text
# 					proxyip_str = proxyip_str + str(child_element.text)
# 			proxyip_str = proxyip_str.replace('None', '')
# 			print proxyip_str
# 			xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 2)
# 			proxyport = content_tree.xpath(xpath_str)
# 			print proxyport[0].text, type(proxyport), len(proxyport)
# 			proxyip_set.add(proxyip[0].text + ':' + proxyport[0].text)
# 		time.sleep(2)

def request_five():
	while 1:
		try:
			target_url = 'http://www.66ip.cn/index.html'
			sleep_time = 43200
			content_str = request_url(target_url)
			#content_str = gzip.GzipFile(fileobj=StringIO(content_gzip), mode="r")
			#content_str = content_str.read().decode('utf-8').encode('utf-8')
			content_str = content_str.decode('utf-8', 'ignore')
			content_buf = StringIO(unicode(content_str))
			parser = etree.HTMLParser()
			content_tree = etree.parse(content_buf, parser = parser)
			basic_xpath_str = '//table[@bordercolor="#6699FF"]/tr[{arg_tr_index}]/td[{arg_td_index}]/text()'
			for tr_index in range(2, 13):
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 1)
				proxyip = content_tree.xpath(xpath_str)
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 2)
				proxyport = content_tree.xpath(xpath_str)
				proxyip_set.add(proxyip[0] + ':' + proxyport[0])
		except Exception, e:
			logging.exception(e)
		finally:
			time.sleep(sleep_time)


def request_six():
	while 1:
		try:
			target_url = 'http://ip.izmoney.com/search/china/high/index.html'
			sleep_time = 1800
			content_gzip = request_url(target_url)
			content_str = gzip.GzipFile(fileobj=StringIO(content_gzip), mode="r")
			content_str = content_str.read().decode('utf-8').encode('utf-8')
			content_str = content_str.decode('utf-8', 'ignore')
			content_buf = StringIO(unicode(content_str))
			parser = etree.HTMLParser()
			content_tree = etree.parse(content_buf, parser = parser)
			basic_xpath_str = '/html/body/div[1]/div[1]/div[2]/div/div/div[2]/table/tbody/tr[{arg_tr_index}]/td[{arg_td_index}]/text()'
			for tr_index in range(1, 26):
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 1)
				proxyip = content_tree.xpath(xpath_str)
				xpath_str = basic_xpath_str.format(arg_tr_index = tr_index, arg_td_index = 2)
				proxyport = content_tree.xpath(xpath_str)
				proxyip_set.add(proxyip[0] + ':' + proxyport[0])
		except Exception, e:
			logging.exception(e)
		finally:
			time.sleep(sleep_time)

def flush_proxyip_bak():
	while 1:
		time.sleep(1800)
		proxyip_file = set()
		proxyip_new = set()
		with open('./proxyips.bak', 'r+') as fd:
			for line in fd.readlines():
				proxyip_file.add(line.strip())
			for proxyip in proxyip_file:
				if proxyip in proxyip_set:
					pass
				else:
					proxyip_new.add(proxyip)
			for proxyip in proxyip_set:
				proxyip_new.add(proxyip)
			with open('./proxyips.bak', 'w+') as fd_write:
				for proxyip in proxyip_new:
					fd_write.write(proxyip + '\n')

def flush_proxyip_from_old():
	while 1:
		time.sleep(43200)
		proxyip_file = set()
		proxyip_new = set()
		with open('./proxyiprank.availability.json', 'r') as fd:
				available_ips = json.load(fd)	
		with open('./proxyips.bak', 'r+') as fd:
			for line in fd.readlines():
				proxyip_file.add(line.strip())
			for proxyip_key, proxyip_value in available_ips.items():
				proxyip_file.add(proxyip_key)
			with open('./proxyips.bak', 'w+') as fd_write:
				for proxyip in proxyip_file:
					fd_write.write(proxyip + '\n')
			logging.info('Add old available ips to prxyips.bak')

first_blood = True
request_one_thread = threading.Thread(target = request_one, args = ())
request_one_thread.start()
request_two_thread = threading.Thread(target = request_two, args = ())
request_two_thread.start()
request_three_thread = threading.Thread(target = request_three, args = ())
request_three_thread.start()
request_four_thread = threading.Thread(target = request_four, args = ())
request_four_thread.start()
request_six_thread = threading.Thread(target = request_six, args = ())
request_six_thread.start()
flush_bak_thread = threading.Thread(target = flush_proxyip_bak, args = ())
flush_bak_thread.start()
flush_old_thread = threading.Thread(target = flush_proxyip_from_old, args = ())
flush_old_thread.start()
if first_blood:
	time.sleep(10)
	first_blood = False
checking_test = ProxyIPRank({}, 5000)
while 1:
	if os.path.isfile('./proxyiprank.availability.json') == True:
			with open('./proxyiprank.availability.json', 'r') as fd:
				available_ips_file = json.load(fd)
				for proxyip_key, proxyip_value in available_ips_file.items():
					proxyip_set.add(proxyip_key)
	if os.path.isfile('./proxyips.bak') == True:
		with open('./proxyips.bak', 'r') as fd:
			for line in fd.readlines():
				proxyip_set.add(line.strip())
	else:
		with open('./proxyips.bak', 'a+') as fd:
			fd.write('')
	proxyip_list = []
	for proxyip in proxyip_set:
		print proxyip
		proxyip_list.append(proxyip)
	proxyip_dict = {}
	for proxyip in proxyip_list:
		spilt_loc = proxyip.find(':')
		ip = proxyip[:spilt_loc]
		port = proxyip[spilt_loc + 1:]
		proxyip_dict[ip] = port
	checking_test.add_proxyip_list(proxyip_dict)
	checking_test.start_check_proxyips()
	checking_test.save_to_disk()
	proxyip_file = set()
	proxyip_new = set()
	for proxyip in proxyip_list:
		if proxyip in proxyip_set:
			proxyip_set.remove(proxyip)
	with open('./proxyips.bak', 'r+') as fd:
		for line in fd.readlines():
			proxyip_file.add(line.strip())
		for proxyip in proxyip_file:
			if proxyip in proxyip_list:
				pass
			else:
				proxyip_new.add(proxyip)
		for proxyip in proxyip_set:
			proxyip_new.add(proxyip)
		with open('./proxyips.bak', 'w+') as fd_write:
			for proxyip in proxyip_new:
				fd_write.write(proxyip + '\n')
	time.sleep(1800)
	



# start_time = time.time()
# proxyip_dict = {}
# fd = open('/root/proxy_ips', 'r')
# for line_index in range(3000):
# 	ip = fd.readline()
# 	port = fd.readline()
# 	proxyip_dict.setdefault(ip.strip(), port.strip())
# fd.close()
# checking_test = ProxyIPRank(proxyip_dict, 5000)
# checking_test.start_check_proxyips()
# print "Using time:", time.time() - start_time
# checking_test.save_to_disk()
# checking_test.add_proxyip_list(proxyip_dict)
# checking_test.start_check_proxyips()