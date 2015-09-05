import socket
import sys, json, binascii

server_ip = ''
server_port = 3000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)
while 1:
	try:
		client_socket, client_addr = server_socket.accept()
		print '###############################################################################'
		print 'Accept: ', client_addr
		with open('./proxyiprank.availability.json', 'r') as fd:
			available_ips = json.load(fd)
			available_ips_str = json.dumps(available_ips, indent = 4)
			client_socket.sendall('{:8x}'.format(binascii.crc32(available_ips_str)))
			print x
			socket_buf_size = 1024
			index = 0
			while available_ips_str:
				client_socket.sendall(available_ips_str[:socket_buf_size])
				available_ips_str = available_ips_str[socket_buf_size:]
				index += 1
				print len(available_ips_str), index

		client_socket.close()


	except Exception, e:
		print "Exception:  ", e
	# finally:
	# 	client_socket.close()

