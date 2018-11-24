import copy

class FogNode():

    def __init__(self, parents=[], resources=[], ip='', epoch=0, seq_number=0, isSendingKeepAlive=False):
        self.ip = ip
        self.resources = resources
        self.epoch = epoch
        self.isReplyingKeepAlive = True
        self.parents = parents  # FogNode()
        self.seq_number = seq_number
        self.isSendingKeepAlive = isSendingKeepAlive

    def ack(self, ip):
        fog = self.getNodeByIp(ip)
        if fog != None:
            fog.isReplyingKeepAlive = True
            fog.isSendingKeepAlive = False


    def sendingKeepAlive(self):
        for parent in self.parents:
            parent.isSendingKeepAlive = True

    def removeInactiveNodes(self):

        for parent in self.parents:
            if parent.isSendingKeepAlive:

                if parent.isReplyingKeepAlive:
                    parent.isReplyingKeepAlive = False
                else:
                    self.parents.remove(parent)


    def updateResource(self, ip='', resources=[], epoch=0):
        fog = self.getNodeByIp(ip)

        if fog != None:
            fog.resources = resources
            fog.epoch = epoch
            return True

        return False

    def insertResource(self, ip='', resources=[], epoch=0):
        fog = self.getNodeByIp(ip)

        if fog == None:
            newfognode = copy.deepcopy(
                FogNode(resources=resources, ip=ip, epoch=epoch))
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
        stringbuilder += '    MY IP: ' + self.ip + '\n'
        stringbuilder += '    MY RESOURCES: ' + str(self.resources) + '\n'
        stringbuilder += '    MY EPOCH: ' + str(self.epoch) + '\n'
        stringbuilder += '    MY IS_REPLYING_KEEPALIVE: ' + str(self.isReplyingKeepAlive) + '\n'
        stringbuilder += '    MY IS_SENDING_KEEPALIVE: ' + str(self.isSendingKeepAlive) + '\n'
        for parent in self.parents:
            stringbuilder += '        IP: ' + parent.ip + '\n'
            stringbuilder += '        RESOURCES: ' + str(parent.resources) + '\n'
            stringbuilder += '        EPOCH: ' + str(parent.epoch) + '\n'
            stringbuilder += '        REPLYING_KEEPALIVE: ' + str(parent.isReplyingKeepAlive) + '\n'
            stringbuilder += '        IS_SENDING_KEEPALIVE: ' + str(parent.isSendingKeepAlive) + '\n'

        return stringbuilder

    def getNodeByIp(self, ip):
        for fog in self.parents:
            if fog.ip == ip:
                return fog

        return None
