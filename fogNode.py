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

    def epochHasChanged(self, epoch):
        for fog in self.fog_nodes:
            if fog.epoch != epoch:
                return True
        return False


if __name__ == '__main__':
    print 'OK'