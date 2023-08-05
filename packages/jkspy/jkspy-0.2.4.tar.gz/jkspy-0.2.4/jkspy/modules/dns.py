import socket

class DNSNode():
    class Meta:
        kinds = ['root', 'node']
        
    def __init__(self, hostname='localhost', kind='node', verbose=False, *args, **kwargs):
        self.ip = socket.gethostname()
        self.hostname = hostname
        self.kind = kind
        if verbose:
            print(">>> Initializing new DNSNode")
            print("    IP :      "+str(self.ip))
            print("    Hostname: "+str(self.hostname))

def startServer():
    new_node = DNSNode(verbose=True)