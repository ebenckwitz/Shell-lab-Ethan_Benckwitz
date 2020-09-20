#! /usr/bin/env python3
#Author: Ethan Benckwitz
import os, sys, re

def main(commands):
    #commands = commands.split()
            if commands[0] == "exit":     #exit program
                sys.exit(1)
            elif not commands:         #no user input will go through loop again
                return
            #command = command.decode().split()
            elif "|" in commands:      #check for pipe command
                pipe_command(commands)
            elif commands[0] == "cd":     #change directories
                #directory = commands.split("cd")[1].strip()
                directory = commands[1]
                try:
                    if len(commands) < 2:
                        os.write(2, ("Provide a directory").encode())
                    else:
                        os.chdir(directory)
                        # os.write(1, (os.getcwd()+"\n").encode())
                except FileNotFoundError:
                    os.write(2, ("File not found! Please try again!\n").encode())
            else:                     #run shell
                #command = command.decode().split()
                my_shell(commands)
    #sys.exit(1)

def my_shell(command):
    pid = os.getpid()
    rc = os.fork()
    args = command

    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:      #child
       # try:
        if '>' in args:
            redirect = command.split('> ')
            os.close(1)
            os.open(redirect[1], os.O_CREAT | os.O_WRONLY);
            os.set_inheritable(1, True)
            exec_command(redirect[0])

        elif '<' in args:
            redirect = command.split('< ')
            os.close(0)
            os.open(redirect[1], os.O_RDONLY);
            os.set_inheritable(0, True)
            exec_command(redirect[0])

        elif '/' in args:    #path names
            program = args[0]
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
        
        else: exec_command(args)

    else:
        if not '&' in args: #background task
            waiting = os.wait()

def pipe_command(command):
    pipe = command.index('|')
    
    pr, pw = os.pipe()
   # for f in (pr, pw):
   #     os.set_inheritable(f, True)
   
    rc = os.fork()
    if rc < 0:
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        os.close(1)         #redirect child's stdout
        os.dup(pw)
        os.set_inheritable(1, True)
        for fd in (pr, pw):
            os.close(fd)
        exec_command(command[0:pipe])
        os.write(2,("%s command not found"%args[0]).encode())
        sys.exit(1)
                  
    else:
        os.close(0)
        os.dup(pr)
        os.set_inheritable(0, True)
        for fd in (pw, pr):
            os.close(fd)
        exec_command(command[pipe + 1:])
        os.write(2,("%s command not found"%args[0]).encode())
        sys.exit(1)
 
def exec_command(args):
    #args = command.split()
    for dir in re.split(":", os.environ['PATH']): #try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ) #try to exec program
        except FileNotFoundError:                #this is expected
            pass                                 #fail quietly
            
    os.write(2, ("Command %s not found. Try again.\n" % args[0]).encode())
    sys.exit(1)                                  #terminate with error

if __name__ == '__main__':
    while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else:
            os.write(1, ("$ ").encode())
        try:
            command = os.read(0, 100)
        except EOFError:
            sys.exit(1)
        except ValueError:
            sys.exit(1)

        command = command.decode().split()
       # for commands in command:
        main(command)

