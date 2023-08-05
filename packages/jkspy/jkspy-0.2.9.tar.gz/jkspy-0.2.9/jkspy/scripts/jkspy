#!/usr/bin/python3
import sys
import jkspy.cmdutils as utils

def help(alert):
    print("\n"+alert)
    print("----------------------------------\nExample:\n----------------------------------")
    print("  root@localhost:~$ jkspy keygen 'keypath/'")
    print("----------------------------------\n")
    
try:
#     print(sys.argv)
    try:
        try:
            utility = getattr(utils, sys.argv[1])
#             print(utility)
            if len(sys.argv) > 2:
                utility(*sys.argv[2:])
            else:
                utility()
        except IndexError:
            help('You should provide a command argument')

    except AttributeError:
        print("Unknown jkspy command '"+sys.argv[1]+"'")
        

except ImportError:
    print("Could not locate library 'jkspy', please install by typing 'pip3 install jkspy'")