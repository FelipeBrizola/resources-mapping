import select
import socket
import struct
import threading
import time
from fogNode import FogNode
from factory import Factory

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
        self.fog = FogNode()
        self.factory = Factory()

    def _senddata(self, writer):
        sentcount = 0
        bufferlen = len(self.write_buffer)

        while sentcount < bufferlen:

            # enviar k.a a cada 30s, enviar well-known/core quando solicitado

            sent = self.sock.sendto(self.write_buffer[sentcount:], self.broadcast_address)
            if sent == 0:
                raise RuntimeError('socket connection broken')
            sentcount += sent
            if sentcount == bufferlen:
                self.write_buffer = ''
                self.writers.remove(writer)

    def _recvdata(self):
        data = ''
        try:
            while True:
                chunk = self.sock.recvfrom(1024)
                if chunk == '':
                    raise RuntimeError('socket connection broken')

                response = self.factory.parseData(data)

                # validar pacote. verificar se eh k.a
                if response.header == 1:
                    if self.fog.epochHasChanged(response.epoch):
                        return True # realiza well-known/core
                
                # validar pacote. verificar se eh resposta do well-known/core

        except:
            pass
        finally:
            if not self.reader_callback == None:
                self.reader_callback(data)

    def cycle(self):
        try:
            self._stop = False
            self.sock.settimeout(1)

            while self._stop == False:
                rlist, wlist, [] = select.select(self.readers, self.writers, [], 1)

                while len(rlist) > 0:
                    self._recvdata()
                    rlist.pop()

                for writer in wlist:
                    self._senddata(writer)

        except Exception as e:
            print 'An error occurred in Synchronizer.cycle()\n' + str(e)

    def close(self):
        try:
            self.sock.close()
            self._stop = True
        except Exception as e:
            print('An error occurred in Listener.close():\n' + str(e))


def callback(message):
    print(message)


if __name__ == '__main__':

    sync = Synchronizer()

    sync.readers.append(sync.sock)
    sync.reader_callback = callback
    listener_thread = threading.Thread(target=sync.cycle)
    listener_thread.start()

    # Wait 3 seconds before broadcasting 0x00
    # time.sleep(3)
    sync.write_buffer = 'Toma esse Broadcast!'
    sync.writers.append(sync.sock)

    # Wait for a timeout period (in case of slow resp) before closing
    # time.sleep(10)
    # sync.close()
