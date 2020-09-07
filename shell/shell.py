#! /usr/bin/env python3
#Author: Ethan Benckwitz
import os, sys, re

command = input("$ ")
while command != "exit":
    my_args = command.split()
    my_shell(my_args[0], my_args[1])
    command = input("S ")
print("It is over.")

def my_shell(arg1, arg2):
    pid = os.getipid()
    os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
    
    rc = os.fork()

    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:      #child
        os.write(1, ("This is a child! Child's pid=%d Parent's pid=%d\n" % (os.getpid(),pid)).encode())
        args = [arg0, arg1]
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
        os.write(1, ("This is a parent! Parent's pid=%d Child's pid=%d\n" % (pid, rc)).encode())
        waiting = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % waiting).enocde())
