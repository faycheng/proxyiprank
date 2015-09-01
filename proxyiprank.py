from __future__ import division
import urllib2
import time
import random
import math
import json
from operator import itemgetter
from multiprocessing.dummy import Pool as ThreadPool

class ProxyIPRank(object):
	"""docstring for ProxyIPRank"""
	proxyip_list = []
	proxyip_rank_dict = {}
	proxyip_check_times = 3
	proxyip_check_times_max = 20
	proxyip_availability_percent = 0.5
	check_timeout = 10
	check_target_url = 'http://www.chengxuyuanfei.com/'
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
	def __init__(self, proxyip_list_arg):
		for proxyip_ip, proxyip_port in proxyip_list_arg.items():
			proxyip_str = str(proxyip_ip) + ':' + str(proxyip_port)
			self.proxyip_list.append(proxyip_str)
		[self.proxyip_rank_dict.setdefault(proxyip, {'avg_time':0.0, 'availability_rate':0.0, 'disperse_rate':0.0, 'check_record':[]}) for proxyip in self.proxyip_list]


	def set_check_times(check_times = 3):
		self.proxyip_check_times = check_times

	def set_availability_percent(availability_percent = 0.95):
		self.proxyip_availability_percent = availability_percent

	def set_target_url(target_url):
		self.check_target_url = target_url

	def set_chect_timeout(timeout):
		self.check_timeout = timeout

	def check_proxyip(self, proxyip):
		check_time = 0
		try:
			print 'checking proxy ip:', proxyip
			proxy_handler = urllib2.ProxyHandler({'http':proxyip})
			proxy_opener = urllib2.build_opener(proxy_handler)
			urllib2.install_opener(proxy_opener)
			req = urllib2.Request(self.check_target_url)
			user_agent_index = random.randint(0, 15)
			req.add_header(self.user_agents[user_agent_index][0], self.user_agents[user_agent_index][1])
			start_time = time.time()
			content = urllib2.urlopen(req, timeout = self.check_timeout).read()
			end_time = time.time()
			check_time =  end_time - start_time
			print check_time
			self.proxyip_rank_dict[proxyip]['check_record'].append(check_time)
			self.proxyip_rank_dict[proxyip]['lastest_check_time'] = time.strftime('%Y.%m.%d-%H:%M:%S', time.localtime(time.time()))
		except Exception, detail:
			print 'Exception Error:', detail
			self.proxyip_rank_dict[proxyip]['check_record'].append(0)
			self.proxyip_rank_dict[proxyip]['lastest_check_time'] = time.strftime('%Y.%m.%d-%H:%M:%S', time.localtime(time.time()))

	def flush_proxyips_dict(self):
		print self.proxyip_rank_dict
		for proxyip, proxyip_check_info in self.proxyip_rank_dict.items():
			for list_index, check_time in enumerate(proxyip_check_info['check_record']):
				print 'check_time:', check_time, 'list_index:', list_index
				if check_time == 0:
					self.proxyip_rank_dict[proxyip]['check_record'][list_index] = self.check_timeout
		print self.proxyip_rank_dict

	def rank_proxyips(self):
		for proxyip, proxyip_check_info in self.proxyip_rank_dict.items():
			self.proxyip_rank_dict[proxyip]['avg_time'] = sum(proxyip_check_info['check_record']) / len(proxyip_check_info['check_record'])
			self.proxyip_rank_dict[proxyip]['availability_rate'] = len([availability for list_index, availability in enumerate(proxyip_check_info['check_record']) if proxyip_check_info['check_record'][list_index] < self.check_timeout]) / len(proxyip_check_info['check_record'])
			for check_time in proxyip_check_info['check_record']:
				self.proxyip_rank_dict[proxyip]['disperse_rate'] += math.pow(check_time - self.proxyip_rank_dict[proxyip]['avg_time'], 2)
			self.proxyip_rank_dict[proxyip]['disperse_rate'] = math.sqrt(self.proxyip_rank_dict[proxyip]['disperse_rate'] / len(proxyip_check_info['check_record']))

	def save_to_disk(self, record_save_path = './proxyiprank.record.json', available_ip_sava_path = './proxyiprank.availability.json'):
		with open(record_save_path, 'a+') as fd:
			fd.write(json.dumps(self.proxyip_rank_dict, indent = 4))
		with open(available_ip_sava_path, 'a+') as fd:
			available_ips = {}
			for proxyip_key, proxyip_value in self.proxyip_rank_dict.items() :
				if proxyip_value['availability_rate'] >= self.proxyip_availability_percent:
					available_ips.setdefault(proxyip_key, proxyip_value)
			json.dump(available_ips, fd, indent = 4)
			
	def start_check_proxyips(self):
		checked_times = 0
		while checked_times < self.proxyip_check_times:
			check_pool = ThreadPool()
			check_pool.map(self.check_proxyip, self.proxyip_list)
			checked_times = checked_times + 1
			check_pool.close()
			check_pool.join()
		self.flush_proxyips_dict()
		self.rank_proxyips()
		print self.proxyip_rank_dict

	

start_time = time.time()
proxyip_dict = {}
fd = open('/root/proxy_ips', 'r')
for line_index in range(50):
	ip = fd.readline()
	port = fd.readline()
	proxyip_dict.setdefault(ip.strip(), port.strip())
fd.close()
checking_test = ProxyIPRank(proxyip_dict)
checking_test.start_check_proxyips()
print "Using time:", time.time() - start_time
checking_test.save_to_disk()
		


