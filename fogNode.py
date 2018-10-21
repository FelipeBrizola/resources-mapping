import copy

class FogNode():
    
    def __init__(self, parents=[], resources=[], ip='', epoch=0, seq_number=0):
        self.ip = ip
        self.resources = resources
        self.epoch = epoch
        self.keepalive_count = 0
        self.parents = parents #FogNode()
        self.seq_number = seq_number

    def updateResource(self, ip, resources, epoch):
        fog = self.getNodeByIp(ip)

        if fog != None:
            fog.resources = resources
            fog.epoch = epoch
            return True

        return False

    def insertResource(self, ip, resources, epoch):
        fog = self.getNodeByIp(ip)

        if fog == None:
            newfognode = copy.deepcopy(FogNode(resources=resources, ip=ip, epoch=epoch))
            self.parents.append(newfognode)
            return True

        return False
            
    def containsResource(self, ip):
        fog = self.getNodeByIp(ip)
        if fog != None:
            return True

        return False

    def epochHasChanged(self, ip, epoch):
        fog = self.getNodeByIp(ip)
        if fog.epoch != epoch:
            return True

        return False

    def checkMyResources(self, resources):
        # TODO: validar recursos e atualizar epoca ou nao
        if len(resources) != len(self.resources):
            self.epoch += 1
            return True

        return False

    def printResources(self):
        stringbuilder = ''
        stringbuilder += 'MY IP: ' + self.ip + '\n'
        stringbuilder += 'MY RESOURCES: ' + str(self.resources) + '\n'
        stringbuilder += 'MY EPOCH: ' + str(self.epoch) + '\n'
        for parent in self.parents:
            stringbuilder += '    IP: ' + parent.ip + '\n'
            stringbuilder += '    RESOURCES: ' + str(parent.resources) + '\n'
            stringbuilder += '    EPOCH: ' + str(parent.epoch) + '\n'

        return stringbuilder

    def getNodeByIp(self, ip):
        for fog in self.parents:
            if fog.ip == ip:
                return fog

        return None


if __name__ == '__main__':
    print 'OK'