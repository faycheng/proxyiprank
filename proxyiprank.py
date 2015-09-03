from __future__ import division
import urllib2
import time
import random
import math
import json
import logging
import threading
import traceback
import socket
import os
from operator import itemgetter
from multiprocessing.dummy import Pool as ThreadPool


class ProxyIPRank(object):
	"""docstring for ProxyIPRank"""
	proxyip_list = []
	proxyip_rank_dict = {}
	proxyip_check_times = 1
	proxyip_check_times_max = 20
	proxyip_availability_percent = 0.5
	check_timeout = 10
	check_target_url = 'http://www.chengxuyuanfei.com/'
	proxyip_log_path = './proxyiprank.log'
	record_save_path = './proxyiprank.record.json', 
	available_ip_sava_path = './proxyiprank.availability.json'
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
	def __init__(self, proxyip_list_arg, port_arg = 3000):
		logging.basicConfig(filename=self.proxyip_log_path, level=logging.INFO, format='%(asctime)s %(levelname)s Func:%(funcName)s Line:%(lineno)s \n\t\t%(message)s', datefmt='%Y.%m.%d  %H:%M:%S')
		logging.info('Start proxyip rank, init ProxyIPRank object')
		for proxyip_ip, proxyip_port in proxyip_list_arg.items():
			proxyip_str = str(proxyip_ip) + ':' + str(proxyip_port)
			self.proxyip_list.append(proxyip_str)
		[self.proxyip_rank_dict.setdefault(proxyip, {'avg_time':0.0, 'availability_rate':0.0, 'disperse_rate':0.0, 'check_record':[]}) for proxyip in self.proxyip_list]
		start_proxyip_server_thread = threading.Thread(target = self.start_proxyip_server, args = (port_arg, ))
		start_proxyip_server_thread.setDaemon(True)
		start_proxyip_server_thread.start()


	def set_check_times(self, check_times = 3):
		self.proxyip_check_times = check_times

	def set_availability_percent(self, availability_percent = 0.95):
		self.proxyip_availability_percent = availability_percent

	def set_target_url(self, target_url):
		self.check_target_url = target_url

	def set_chect_timeout(self, timeout):
		self.check_timeout = timeout

	def set_proxyip_log_path(self, log_path):
		self.proxyip_log_path = log_path

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
			#logging.info(proxyip + '\tsucceeded')
			time.sleep(3)
		except Exception, e:
			print e
			self.proxyip_rank_dict[proxyip]['check_record'].append(0)
			self.proxyip_rank_dict[proxyip]['lastest_check_time'] = time.strftime('%Y.%m.%d-%H:%M:%S', time.localtime(time.time()))
			#logging.info(proxyip + '\tfailed')
			#logging.exception(e.args)
			time.sleep(3)


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
		self.record_save_path = record_save_path
		self.available_ip_sava_path = available_ip_sava_path
		if os.path.isfile(record_save_path) == False:
			with open(record_save_path, 'a+') as fd:
				fd.write(json.dumps(self.proxyip_rank_dict))
				logging.info('Save proxyiprank record to ' + record_save_path)
		else:
			with open(record_save_path, 'a+') as fd:
				proxyip_rank_dict_file = json.load(fd)
				for proxyip_key, proxyip_value in self.proxyip_rank_dict.items():
					proxyip_rank_dict_file[proxyip_key] = proxyip_value
				with open(record_save_path, 'w') as fd_tmp:
					fd_tmp.write(json.dumps(proxyip_rank_dict_file))
				logging.info('Save proxyiprank record to ' + record_save_path)
		if os.path.isfile(available_ip_sava_path) == False:
			with open(available_ip_sava_path, 'a+') as fd:
				available_ips = {}
				for proxyip_key, proxyip_value in self.proxyip_rank_dict.items() :
					if proxyip_value['availability_rate'] >= self.proxyip_availability_percent:
						available_ips[proxyip_key] = proxyip_value
				json.dump(available_ips, fd, indent = 4)
				logging.info('Save available proxyips to ' + available_ip_sava_path)
		else:
			with open(available_ip_sava_path, 'r') as fd:
				available_ips_file = json.load(fd)
				available_ips = {}
				for proxyip_key, proxyip_value in self.proxyip_rank_dict.items() :
					if proxyip_value['availability_rate'] >= self.proxyip_availability_percent:
						available_ips_file[proxyip_key] = proxyip_value
				with open(available_ip_sava_path, 'w') as fd_tmp:
					json.dump(available_ips_file, fd_tmp, indent = 4)
				logging.info('Save available proxyips to ' + available_ip_sava_path)
		# with open(record_save_path, 'a+') as fd:
		# 	proxyip_rank_dict_file = json.load(fd)
		# 	for proxyip_key, proxyip_value in self.proxyip_rank_dict.items():
		# 		proxyip_rank_dict_file[proxyip_key] = proxyip_value
		# 	with open(record_save_path, 'w') as fd_tmp:
		# 		fd_tmp.write(json.dumps(proxyip_rank_dict_file))
		# 	logging.info('Save proxyiprank record to ' + record_save_path)
		# with open(available_ip_sava_path, 'r') as fd:
		# 	available_ips_file = json.load(fd)
		# 	available_ips = {}
		# 	for proxyip_key, proxyip_value in self.proxyip_rank_dict.items() :
		# 		if proxyip_value['availability_rate'] >= self.proxyip_availability_percent:
		# 			available_ips_file[proxyip_key] = proxyip_value
		# 	with open(available_ip_sava_path, 'w') as fd_tmp:
		# 		json.dump(available_ips_file, fd_tmp, indent = 4)
		# 	logging.info('Save available proxyips to ' + available_ip_sava_path)
		

	def start_check_proxyips(self):
		checked_times = 0
		while checked_times < self.proxyip_check_times:
			# check_pool = ThreadPool()
			# check_pool.map(self.check_proxyip, self.proxyip_list)
			# checked_times = checked_times + 1
			# check_pool.close()
			# check_pool.join()
			threads = []
			for index in range(len(self.proxyip_list)):
				tmp = self.proxyip_list[index]
				check_thread = threading.Thread(target = self.check_proxyip, args = (tmp,))
				threads.append(check_thread)
			for index in range(len(self.proxyip_list)):
				threads[index].start()
			for index in range(len(self.proxyip_list)):
				threads[index].join()
			checked_times = checked_times + 1
		self.flush_proxyips_dict()
		self.rank_proxyips()
		#[availability for list_index, availability in enumerate(proxyip_check_info['check_record']) if proxyip_check_info['check_record'][list_index] < self.check_timeout]
		logging.info('Checked ' + str(len(self.proxyip_rank_dict)) + ' ips. ' + str(len([available_ip for available_ip, proxyip_check_info in self.proxyip_rank_dict.items() if proxyip_check_info['availability_rate'] >= self.proxyip_availability_percent]))+ ' is available.')
		print self.proxyip_rank_dict

	def start_proxyip_server(self, port_arg = 3000):
		server_ip = ''
		server_port = port_arg
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.bind((server_ip, server_port))
		while True:
			try:
				client_message, client_address = server_socket.recvfrom(1024)
				print client_address
				logging.info('Accept client: ' + client_address[0])
				send_json_thread = threading.Thread(target = self.send_json_to_client, args = (server_socket, client_address))
				send_json_thread.start()
				# with open(self.available_ip_sava_path, 'r') as fd:
				# 	available_ips = json.load(fd)
				# # for proxyip_key, proxyip_value in self.proxyip_rank_dict.items() :
				# # 	if proxyip_value['availability_rate'] >= self.proxyip_availability_percent:
				# # 		available_ips.setdefault(proxyip_key, proxyip_value)
				# available_ips_str = json.dumps(available_ips, indent = 4)
				# server_socket.sendto(available_ips_str, client_address)
				# logging.info('Send successful')
			except Exception, e:
				print 'Exception: ', e
				logging.exception(e)
			#time.sleep(1)

	def send_json_to_client(self, server_socket, client_address):
		try:
			print 'send_json_to_client', server_socket, client_address
			with open(self.available_ip_sava_path, 'r') as fd:
				available_ips = json.load(fd)
				# for proxyip_key, proxyip_value in self.proxyip_rank_dict.items() :
				# 	if proxyip_value['availability_rate'] >= self.proxyip_availability_percent:
				# 		available_ips.setdefault(proxyip_key, proxyip_value)
				available_ips_str = json.dumps(available_ips, indent = 4)
				server_socket.sendto(available_ips_str, client_address)
				logging.info('Send successful')
		except Exception, e:
			print 'Exception: ', e
			logging.exception(e)


	

start_time = time.time()
proxyip_dict = {}
fd = open('/root/proxy_ips', 'r')
for line_index in range(3000):
	ip = fd.readline()
	port = fd.readline()
	proxyip_dict.setdefault(ip.strip(), port.strip())
fd.close()
checking_test = ProxyIPRank(proxyip_dict)
checking_test.start_check_proxyips()
print "Using time:", time.time() - start_time
checking_test.save_to_disk()
checking_test.start_proxyip_server()
		


