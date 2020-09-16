#! /usr/bin/env python3
#Author: Ethan Benckwitz
import os, sys, re

def main():
    while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else:
            os.write(1, ("$ ").encode())
        try:
            command = input()
        except EOFError:
            sys.exit(1)
            
        if command == "exit":     #exit program
            break
        
        elif not command:         #no user input will go through loop again
            pass
        
        elif '|' in command:      #check for pipe command
            pipe_command(command)
        elif 'cd' in command[0]:     #change directories
            directory = command.split("cd")[1].strip()
            try:
                if len(command) > 2:
                    os.write(2, ("Too many arguments").encode())
                elif len(command) < 2:
                    os.write(2, ("Provide a directory").encode())
                else:
                    os.chdir(directory)
                    os.write(1, (os.getcwd()+"\n").encode())
            except FileNotFoundError:
                os.write(2, ("File not found! Please try again!\n").encode())
        else:                     #run shell
            my_shell(command)
    sys.exit(1)

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

        if '<' in args:
            redirect = command.split('< ')
            os.close(0)
            os.open(redirect[1], os.O_RDONLY);
            os.set_inheritable(0, True)
            exec_command(redirect[0])

        if '/' in args[0]:    #path names
            program = args[0]
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
        
        exec_command(args)
    else:
        if not '&' in args: #background task
            waiting = os.wait()

def pipe_command(command):
    cmd1, cmd2 = command.split('|')    
    pr, pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f, True)

    rc = os.fork()
    if rc < 0:
        print("fork failed, returning %d\n" %rc, file=sys.stderr)
        sys.exit(1)

    elif rc == 0:
        os.close(1)         #redirect child's stdout
        fd = os.dup(pw)
        os.set_inheritable(1, True)
        for fd in (pr, pw):
            os.close(fd)
        exec_command(command[:command.index('|')])
                  
    else:
        os.close(0)
        fd = os.dup(pr)
        os.set_inheritable(0, True)
        for fd in (pw, pr):
            os.close(fd)
        exec_command(command[command.index('|') + 1:])

def exec_command(command):
    args = command.split()
    for dir in re.split(":", os.environ['PATH']): #try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ) #try to exec program
        except FileNotFoundError:                #this is expected
            pass                                 #fail quietly
            
    os.write(2, ("Command %s not found. Try again.\n" % args[0]).encode())
    sys.exit(1)                                  #terminate with error

if __name__ == '__main__':
main()
