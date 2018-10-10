class Factory():

    def __init__(self):
        pass

    def parseData(self, data):
        
        # split dos doados
        response = Response(data[0], data[1])
        return response

        


class Response():

    def __init__(self, header, epoch):
        self.header = header
        self.epoch = epoch