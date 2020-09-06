#! /usr/bin/env python3

import os, sys, re


rc = os.fork()

if rc < 0:
    os.write(2, ("Fork failed, returning %d\n" % rc).encode())
    sys.exit(1)

elif rc == 0:      #child
    os.write(1, ("Child\n").encode())
    #args = ?
    for dir in re.split(":", os.environ['PATH']): #try each directory in the path
        program = "%s/%s" % (dir, args[0])
        os.write(1, ("Child is trying to exec %s\n" % program).encode())
        try:
            os.execve(program, args, os.environ) #try to exec program
        except FileNotFoundError:                #this is expected
            pass                                 #fail quietly
        break
    os.write(2, ("Child was not able to exec %s\n" % args[0]).encode())
    sys.exit(1)                                  #terminate with error

else:
    os.write(1, ("Parent\n").encode())
    waiting = os.wait()
    os.write(1, ("Parent: Child %d terminated with exit code %d\n" % waiting).enocde())



        
