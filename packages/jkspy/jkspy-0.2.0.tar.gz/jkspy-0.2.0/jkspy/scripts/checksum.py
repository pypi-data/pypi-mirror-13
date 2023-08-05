#!/usr/bin/python3
import sys
try:
    from jkspy.modules.hash import get_checksum

    def help(alert):
        print("\n"+alert)
        print("----------------------------------\nExample:\n----------------------------------")
        print("  root@localhost:~$ checksum /home/user/downloaded.zip sha256")
        print("----------------------------------\n")
    
    try:
        print(get_checksum(*sys.argv[1:]))
    except FileNotFoundError:
        help("File [ "+sys.argv[1]+" ] could not be found. Please type the correct path.")
    except AttributeError:
        help("[ "+sys.argv[2]+" ] is not a supported algorithm")

except ImportError:
    print("Could not locate library 'jkspy', please install by typing 'pip3 install jkspy'")