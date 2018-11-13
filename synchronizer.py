import select
import socket
import struct
import threading
import time
import sys
import getopt
from fogNode import FogNode
from factory import Factory

from coapthon.client.helperclient import HelperClient

# protocoltype 16 bits
# message type = req ou response 16 bits -  ack ou k.a
# seq number int 64bits
# epoca int 64bits
# hash md5 128 bits
# multicast

class Synchronizer():

    def __init__(self, fog):

        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # self.sock.bind(('', 9090))
        # self.broadcast_address = ('255.255.255.255', 9090)

        self.broadcast_address = ('239.255.4.3', 1234)
        self.sock = self.create_socket('239.255.4.3', 1234)
        self.fog = fog
        self.factory = Factory()

    def create_socket(self, multicast_ip, port):
        """
        Creates a socket, sets the necessary options on it, then binds it. The socket is then returned for use.
        """

        local_ip = socket.gethostbyname(socket.gethostname())

        # create a UDP socket
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # allow reuse of addresses
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # set multicast interface to local_ip
        my_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_ip))

        # Set multicast time-to-live to 2...should keep our multicast packets from escaping the local network
        my_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        # Construct a membership request...tells router what multicast group we want to subscribe to
        membership_request = socket.inet_aton(multicast_ip) + socket.inet_aton(local_ip)

        # Send add membership request to socket
        # See http://www.tldp.org/HOWTO/Multicast-HOWTO-6.html for explanation of sockopts
        my_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)

        my_socket.bind(('', port))
        
        return my_socket

    def senddata(self, data, address):

        sent = self.sock.sendto(data, address)
        if sent == 0:
            raise RuntimeError('socket connection broken')

        return sent

    def recvdata(self):
        datagram = ''
        try:
            while True:
                datagram, address = self.sock.recvfrom(1024)
                if address == '':
                    raise RuntimeError('socket connection broken')

                if address[0] == self.fog.ip: #myself
                    continue

                response = self.factory.parse_response(datagram)

                # reseta contador - ACK
                if response.messagetype == 'ack':
                    self.fog.keepalive_count = 0

                # validar pacote. verificar se eh k.a
                if response.messagetype == 'keepalive':

                        # valida se deve inserir novo nodo ou atualizar
                        if self.fog.containsResource(ip=address[0]):

                            # utiliza epoch recebida para validar se houve alteracoes
                            if self.fog.epochHasChanged(ip=address[0], epoch=response.epoch):

                                # se houve alteracoes(atualizacao de recurso). realiza requisicao coap
                                client = HelperClient(server=(address[0], 5683))
                                responseCoap = client.get('/.well-known/core')

                                # utiliza epoca do recurso que foi recebido por broadcast
                                self.fog.updateResource(ip=responseCoap.source[0], resources=responseCoap.payload, epoch=response.epoch)

                        # utiliza epoca do recurso que foi recebido por broadcast
                        # se houve alteracoes(inclusao de novo nodo). realiza requisicao coap
                        else:
                            client = HelperClient(server=(address[0], 5683))

                            # tratar timeout
                            responseCoap = client.get('/.well-known/core')
                            if responseCoap == None:
                                pass
                            self.fog.insertResource(ip=responseCoap.source[0], resources=responseCoap.payload, epoch=response.epoch)

                        # responde ACK para qm enviou o ka.
                        datagram = self.factory.build_request(epoch=self.fog.epoch, seq_number=self.fog.seq_number, message_type='ack')
                        self.senddata(datagram, address)

        except socket.timeout as error:
            print 'timeout'
            print error.message
            self.fog.keepalive_count += 1

        except Exception as error:
            self.sock.close()

    def observer(self):
        # busca em coapserver os proprios recursos
        # frequentemente realizar esse request para se monitorar.
        # caso haja alteracoes nos recursos, incrementar epoca        

        print 'observer'
        client = HelperClient(server=(self.fog.ip, 5683))
        responseCoap = client.get('/.well-known/core')

        if responseCoap.payload == None:
            responseCoap.payload = []

        # atualiza epoca se estiver diferente
        self.fog.checkMyResources(responseCoap.payload)
        self.fog.resources = responseCoap.payload

        time.sleep(20)
        return self.observer()

    def keepalive(self):
        print 'send keepalive'
        datagram = self.factory.build_request(epoch=self.fog.epoch, seq_number=self.fog.seq_number, message_type='keepalive')
        self.senddata(datagram, self.broadcast_address)
        time.sleep(10)
        return self.keepalive()

    def worker(self):

        worker_server_address = (socket.gethostbyname(socket.gethostname()), 5001)
        sock_worker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_worker.bind(worker_server_address)

        print 'sync worker running on address: ' + str(worker_server_address[0]) + ' and port ' + str(worker_server_address[1])

        while True:
            try:
                data, client_address = sock_worker.recvfrom(1024)
                operation = data[0]

                if operation == 'p':
                    sock_worker.sendto(self.fog.printResources(), client_address)  
                    continue
                else:
                    sock_worker.sendto('Missing params', client_address)
                    continue

            except socket.timeout:
                print 'TIMEOUT'
                continue    
    
if __name__ == '__main__':

    fognode = FogNode(ip=socket.gethostbyname(socket.gethostname()))
    sync = Synchronizer(fognode)
    
    threading.Thread(target=sync.recvdata).start()
    threading.Thread(target=sync.keepalive).start()
    threading.Thread(target=sync.observer).start()
    threading.Thread(target=sync.worker).start()

    while True:
        time.sleep(1)
