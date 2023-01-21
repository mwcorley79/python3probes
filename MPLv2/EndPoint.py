class EndPoint:
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port 
        
    def __str__(self):
        return str(self.ip + ":" + str(self.port))

       