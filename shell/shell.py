#! /usr/bin/env python3
#Author: Ethan Benckwitz
import os, sys, re

def beginning():
    while True:
        if 'PS1' in os.environ:
            os.write(1, os.envrion['PS1'].encode())
            
        command = input('$ ')
        if command == "exit":     #exit program
            break
        elif not command:         #no user input will go through loop again
            pass
        elif 'cd' in command:     #change directories
            directory = command.split("cd")[1].strip()
            try:
                os.chdir(directory)
                os.write(1, (os.getcwd()+"\n").encode())
            except FileNotFoundError:
                os.write(2, ("File not found! Please try again!\n").encode())
        else:                     #run shell
            my_shell(command)
    sys.exit(1)

def my_shell(command):
    pid = os.getpid()
    #os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
    
    rc = os.fork()
    args = command.split()

    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:      #child
       # os.write(1, ("This is a child! Child's pid=%d Parent's pid=%d\n" % (os.getpid(),pid)).encode())
       # try:
            
        if '>' in args:
            redirect = command.split('> ')
            os.close(1)
            os.open(redirect[1], os.O_CREAT | os.O_WRONLY);
            os.set_inheritable(1, True)
            args.remove(redirect[1])
            args.remove('>')

        if '<' in args:
            redirect = command.split('< ')
            os.close(0)
            os.open(redirect[1], os.O_RDONLY);
            os.set_inheritable(0, True)
            args.remove('<')
        #except FileNotFoundError:
         #   os.write(2, ("File not found!\n").encode())
            
        for dir in re.split(":", os.environ['PATH']): #try each directory in the path
            program = "%s/%s" % (dir, args[0])
            #os.write(1, ("Child is trying to exec %s\n" % program).encode())
            try:
                os.execve(program, args, os.environ) #try to exec program
            except FileNotFoundError:                #this is expected
                pass                                 #fail quietly
            
        os.write(2, ("Command %s not found. Try again.\n" % args[0]).encode())
        sys.exit(1)                                  #terminate with error

    else:
       # os.write(1, ("This is a parent! Parent's pid=%d Child's pid=%d\n" % (pid, rc)).encode())
        waiting = os.wait()
       #os.write(1, ("Parent: Child %d terminated with exit code %d\n" % waiting).encode())
        
beginning()
