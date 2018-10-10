import select
import socket
import struct
import threading
import time
from fogNode import FogNode
from factory import Factory

from coapthon.client.helperclient import HelperClient


class Synchronizer():

    def __init__(self):
        address = ('0.0.0.0', 9090)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(address)
        self.readers = []
        self.writers = []
        self.reader_buffer = ''
        self.write_buffer = ''
        self.reader_callback = None
        self.quit = False
        self.broadcast_address = address
        self.observer()
        self.fog = None

        self.factory = Factory()

    def senddata(self, writer):
        sentcount = 0
        bufferlen = len(self.write_buffer)

        while sentcount < bufferlen:

            # enviar k.a a cada 30s

            sent = self.sock.sendto(self.write_buffer[sentcount:], self.broadcast_address)
            if sent == 0:
                raise RuntimeError('socket connection broken')
            sentcount += sent
            if sentcount == bufferlen:
                self.write_buffer = ''
                self.writers.remove(writer)

    def recvdata(self):
        datagram = ''
        try:
            while True:
                datagram, address = self.sock.recvfrom(1024)
                if address == '':
                    raise RuntimeError('socket connection broken')

                response = self.factory.parseData(datagram)

                # validar pacote. verificar se eh k.a
                if response.header == '1':

                        # valida se deve inserir novo nodo ou atualizar
                        if self.fog.containsResource(ip=address[0]):

                            # utiliza epoch recebida para validar se houve alteracoes
                            if self.fog.epochHasChanged(ip=address[0], epoch=response.epoch):

                                # se houve alteracoes(atualizacao de recurso). realiza requisicao coap
                                client = HelperClient(server=(address[0], 5683))
                                responseCoap = client.get('/.well-known/core')

                                # utiliza epoca do recurso que foi recebido por broadcast
                                self.fog.updateResource(ip=responseCoap.source[0], resources=responseCoap.payload, epoch=response.epoch)

                        else:
                            # utiliza epoca do recurso que foi recebido por broadcast
                            # se houve alteracoes(inclusao de novo nodo). realiza requisicao coap
                            client = HelperClient(server=(address[0], 5683))
                            responseCoap = client.get('/.well-known/core')
                            self.fog.insertResource(ip=responseCoap.source[0], resources=responseCoap.payload, epoch=response.epoch)

                    # TODO: Responder ACK para que quem enviou o k.a saiba que 'eu' ainda estou em operaca
                            

        except:
            pass
        finally:
            if not self.reader_callback == None:
                self.reader_callback(datagram)

    def cycle(self):
        try:
            self._stop = False
            self.sock.settimeout(1)

            while self._stop == False:
                rlist, wlist, [] = select.select(self.readers, self.writers, [], 1)

                while len(rlist) > 0:
                    self.recvdata()
                    rlist.pop()

                for writer in wlist:
                    self.senddata(writer)

        except Exception as e:
            print 'An error occurred in Synchronizer.cycle()\n' + str(e)

    def close(self):
        try:
            self.sock.close()
            self._stop = True
        except Exception as e:
            print('An error occurred in Listener.close():\n' + str(e))

    def observer(self):
        # busca em coapserver os proprios recursos
        # frequentemente realizar esse request para se monitorar.
        # caso haja alteracoes nos recursos, incrementar epoca
        # provavelmente precise colocar numa thread
        client = HelperClient(server=('127.0.0.1', 5683))
        responseCoap = client.get('/.well-known/core')

        if self.fog == None:
            self.fog = FogNode(resources=responseCoap.payload, ip='127.0.0.1')
        else:
            self.fog.checkMyResources(responseCoap.payload)

        time.sleep(10)
        self.observer()



def callback(message):
        print 'callback ---'
        print(message)
        print 'callback ---'


if __name__ == '__main__':

    sync = Synchronizer()
    
    sync.readers.append(sync.sock)
    sync.reader_callback = callback
    listener_thread = threading.Thread(target=sync.cycle)
    listener_thread.start()
    sync.readers.append(sync.sock)

    # time.sleep(3)
    # sync.write_buffer = '12'
    # sync.writers.append(sync.sock)

    # Wait for a timeout period (in case of slow resp) before closing
    time.sleep(20)
    sync.close()
