class FogNode():
    
    def __init__(self):
        self.ip = ''
        self.resources = []
        self.epoch = 0
        self.is_replying_keepalive = True
        self.fog_nodes = [] # self.fogs()

    def updateResource(self):
        return True

    def insertResource(self):
        return True

    def containsResource(self):
        return True

if __name__ == '__main__':
    print 'OK'