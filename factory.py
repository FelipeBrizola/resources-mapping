# protocoltype 16 bits ===> 0x13 ----short
# message type = req ou response 16 bits -  ack ou k.a  ===> 0x14 0x15 -----short
# seq number int 64bits 0x16 0x17 0x18 0x19 0x20 0x21 0x22 0x23 ----- double
# epoca int 64bits ----- double
# hash md5 128 ---- bits 2doubles
# multicast

import md5
from struct import *

class Factory():

    def __init__(self):
        pass

    def parse_response(self, stream):
        hash = stream[20:]
        stream = stream[:20]

        # envalid data
        if md5.new(stream).hexdigest() != hash:
            return None

        return Response(protocoltype=stream[:2], messagetype=stream[2:4], seq_number=stream[4:12], epoch=stream[12:], hash=hash)

    def build_request(self, epoch, seq_number, message_type):
        protocoltype = 0x13

        if  message_type == 'ack':
            message_type = 0x14
        elif message_type == 'keepalive':
            message_type = 0x15

        stream = pack('>hhQQ',protocoltype, message_type, seq_number, epoch)
        hash = md5.new(stream).hexdigest()
        return stream + hash
        


class Response():

    def __init__(self, protocoltype, messagetype, seq_number, epoch, hash):
        self.protocoltype = protocoltype
        self.seq_number = seq_number
        self.epoch = epoch
        self.hash = hash

        if messagetype == '\x00\x14':
            self.messagetype = 'ack'
        elif messagetype == '\x00\x15':
            self.messagetype = 'keepalive'


# keepalive e ack
class Request():
    
    def __init__(self, protocoltype, messagetype, seq_number, epoch, hash):
        self.protocoltype = protocoltype
        self.messagetype = messagetype
        self.seq_number = seq_number
        self.epoch = epoch
        self.hash = hash


if __name__ == '__main__':
    factory = Factory()
    stream = factory.build_request(epoch=1, seq_number=15, message_type='keepalive')
    print ':'.join(x.encode('hex') for x in stream)
    response = factory.parse_response(stream)
    print 'PROTO TYPE: ', response.protocoltype
    print 'MESSAGE TYPE: ', response.messagetype
    print 'SEQ NUMBER: ', response.seq_number
    print 'EPOCH: ', response.epoch
    print 'HASH: ', response.hash
