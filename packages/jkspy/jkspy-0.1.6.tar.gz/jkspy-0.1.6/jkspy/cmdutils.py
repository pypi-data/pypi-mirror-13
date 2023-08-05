import sys
from jkspy.modules import hash
from Crypto.PublicKey import RSA
from jkspy.helpers import readFile, writeFile

def test():
    print(">>> Running jkspy TEST")
    for i in range(0, 10):
        print(i)
    print(">>> TEST Completed")
    
def checksum(filepath, *options):
    try:
        print(hash.get_checksum(filepath, *options))
    except TypeError:
        print("Please provide a filepath.")
        print("  (Example)  >> jkspy checksum test.txt")

def keygen(filepath, kind=16, format='PEM'):
    if int(kind) > 0:
        keyfile = open(filepath, 'wb')
        keyfile.write(hash.make_key(int(kind)))
        keyfile.close()
        print("New random key created at "+filepath)
    elif kind == 'pair':
        keypair = hash.make_keypair()
        hash.save_keypair(keypair, filepath, format)
        print("New keypair created as "+filepath+'.private and '+filepath+'.public')
    
def encrypt(pubkeypath, filepath):
    pubkey = hash.open_keypair(pubkeypath)
    content = readFile(filepath)
    
    crypto = hash.encrypt(pubkey, content)
    
    writeFile(filepath+'.secret', crypto, True)
    
def decrypt(prvkeypath, filepath):
    try:
        prvkey = hash.open_keypair(prvkeypath)
        content = readFile(filepath, True)
        
        plain = hash.decrypt(prvkey, content).decode()
        
        writeFile(filepath+'.plain', plain)
    except ValueError:
        print("Could not decrypt ["+filepath+"]")