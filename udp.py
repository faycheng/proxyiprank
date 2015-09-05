import socket, json

server_ip = ''
server_port = 3000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((server_ip, server_port))
client_message, client_address = server_socket.recvfrom(1024)
print client_address
print 'send_json_to_client', server_socket, client_address
with open('./proxyiprank.availability.json', 'r') as fd:
	available_ips = json.load(fd)
	# for proxyip_key, proxyip_value in self.proxyip_rank_dict.items() :
	# 	if proxyip_value['availability_rate'] >= self.proxyip_availability_percent:
	# 		available_ips.setdefault(proxyip_key, proxyip_value)
	available_ips_str = json.dumps(available_ips, indent = 4)
	print available_ips_str
	# server_socket.sendto(str(len(available_ips_str)), client_address)
	socket_buf_size = 1024
	index = 0
	while available_ips_str:
		server_socket.sendto(available_ips_str[:socket_buf_size], client_address)
		available_ips_str = available_ips_str[socket_buf_size:]
		index += 1
		print len(available_ips_str), index

