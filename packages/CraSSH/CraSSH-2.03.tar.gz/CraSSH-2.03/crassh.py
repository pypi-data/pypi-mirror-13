#!/usr/bin/env python
# coding=utf-8

"""
    Nick Bettison

    Python script to automate running commands on switches.

    Cisco Remote Automation via Secure Shell... or C.R.A.SSH for short!

    Use the -h for help

    - www.linickx.com

"""

# Import libs
import getpass
import paramiko
import socket
import time
import datetime
from io import StringIO
import sys, getopt
import os, stat
import re

# Version Control in a Variable
crassh_version = "2.03"

# Python 2 & 3 input compatibility
try:
    input = raw_input
except NameError:
    pass

# Functions

# # http://blog.timmattison.com/archives/2014/06/25/automating-cisco-switch-interactions/
def send_command(command = "show ver", hostname = "Switch", bail_timeout = 60):
    
    global remote_conn, remote_conn_pre
    
    # Start with empty var & loop
    output = ""
    keeplooping = True

    # Regex for either config or enable
    regex = '^' + hostname + '(.*)(\ )?#'
    theprompt = re.compile(regex)

    # Time when the command started, prepare for timeout.
    now = int(time.time())
    timeout = now + bail_timeout

    # Send the command
    remote_conn.send(command + "\n")

    # loop the output
    while keeplooping:

        # Setup bail timer
        now = int(time.time())
        if now == timeout:
            print("\n Command %s took %s secs to run, bailing!" % (cmd, str(bail_timeout)))
            output += "crassh bailed on command: " + cmd
            keeplooping = False
            break

        # update receive buffer whilst waiting for the prompt to come back
        if remote_conn.recv_ready():
            output += remote_conn.recv(2048).decode('utf-8')

            # Search the output for our prompt
            theoutput = output.splitlines()
            for lines in theoutput:
                myregmatch = theprompt.search(lines)

            if myregmatch:
                keeplooping = False

    return output

# Check Commands for dangerous things
def do_no_harm(command):

    harmful = False

    if re.match("rel", command):
        harmful = True
        error = "reload"

    if re.match("wr(.*)\ e", command):
        harmful = True
        error = "write erase"

    if re.match("del", command):
        harmful = True
        error = "delete"

    if harmful:
        print("")
        print("Harmful Command found - Aborting!")
        print("  \"%s\" tripped the do no harm sensor => %s" % (command, error))
        print("\n To force the use of dangerous things, use -X")
        print_help()

def print_help(exit = 0):
    global crassh_version
    
    print("\n Usage: %s -s switches.txt -c commands.txt -p -w -t 45 -e" % sys.argv[0])
    print("   -s supply a text file of switch hostnames or IP addresses [optional]")
    print("   -c supply a text file of commands to run on switches [optional]")
    print("   -w write the output to a file [optional | Default: True]")
    print("   -p print the output to the screen [optional | Default: False]")
    print("   -pw is supported, will print the output to screen and write the output to file! [optional]")
    print("   -t set a command timeout in seconds [optional | Default: 60]")
    print("   -X disable \"do no harm\" [optional]")
    print("   -e set an enable password [optional]")
    print("   -d set a delay (in seconds) between commands [optional]")
    print("   -A set an Authentication file for SSH credentials [optional]")
    print("   -U set a Username for SSH Authentication [optional]")
    print("   -P set a Password for SSH Authentication [optional]")
    print(" ")
    print("Version: %s" % crassh_version)
    print(" ")
    sys.exit(exit)

# http://stackoverflow.com/questions/1861836/checking-file-permissions-in-linux-with-python
def isgroupreadable(filepath):
  st = os.stat(filepath)
  return bool(st.st_mode & stat.S_IRGRP)

def isotherreadable(filepath):
  st = os.stat(filepath)
  return bool(st.st_mode & stat.S_IROTH)

# Read lines of a text file
def readtxtfile(filepath):
    
    if os.path.isfile(filepath) == False:
        print("Cannot find %s" % filepath)
        sys.exit()
    # setup return array
    txtarray = []
    # open our file
    f=open(filepath,'r')
    # Loop thru the array
    for line in f:
        # Append each line to array
        txtarray.append(line.strip())
    return txtarray

# Read a Crassh Authentication File
def readauthfile(filepath):
    
    if os.path.isfile(filepath) == False:
        print("Cannot find %s" % filepath)
        sys.exit()
        
    f=open(filepath,'r')
    # Loop thru the array
    for fline in f:
        thisline = fline.strip().split(":")
        if thisline[0].strip() == "username":
            username = thisline[1].strip()
        if thisline[0].strip() == "password":
            if isgroupreadable(filepath):
                print("** Password not read from %s - file is GROUP readable ** " % filepath)
            else:
                if isotherreadable(filepath):
                    print("** Password not read from %s - file is WORLD readable **"% filepath)
                else:
                    password = thisline[1].strip()
                    return username, password

# Get Connect and get Hostname of Cisco Device
def connect(device = "127.0.0.1", username = "cisco", password = "cisco", enable = False, enable_password = "cisco"):
    
    global remote_conn_pre, remote_conn
    
    """
        https://pynet.twb-tech.com/blog/python/paramiko-ssh-part1.html

    """

    remote_conn_pre = paramiko.SSHClient()

    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("Connecting to %s ... " % device)

    try:
        # http://yenonn.blogspot.co.uk/2013/10/python-in-action-paramiko-handling-ssh.html
        remote_conn_pre.connect(device, username=username, password=password, allow_agent=False, look_for_keys=False)
    except paramiko.AuthenticationException as e:
        print("Authentication Error: %s" % e)
        sys.exit()
    except paramiko.SSHException as e:
        print("SSH Error: %s" % e)
        sys.exit()
    except socket.error as e:
        print("Connection Failed: %s" % e)
        sys.exit()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        sys.exit()

    remote_conn = remote_conn_pre.invoke_shell()

    # Flush buffer.
    output = remote_conn.recv(1000)

    if enable:
        remote_conn.send("enable\n")
        time.sleep(0.5)
        remote_conn.send(enable_password + "\n")

    remote_conn.send("terminal length 0\n")
    time.sleep(0.5)
    # Flush buffer.
    output = remote_conn.recv(1000)

    # Clear the Var.
    output = ""

    remote_conn.send("show run | inc hostname \n")
    while not "#" in output:
        # update receive buffer
            output += remote_conn.recv(1024).decode('utf-8')

    for subline in output.splitlines():
        thisrow = subline.split()
        try:
            gotdata = thisrow[1]
            if thisrow[0] == "hostname":
                hostname = thisrow[1]
                prompt = hostname + "#"
        except IndexError:
            gotdata = 'null'
            
    return hostname

def disconnect():
    global remote_conn_pre
    remote_conn_pre.close()

# Main Code Block
def main():
    
    # import Global Vars
    global input
    
    # Main Vars (local scope)
    switches = []
    commands = []
    filenames = []
    sfile=''
    cfile=''
    play_safe = True
    enable = False
    delay_command = False
    writeo = True
    printo = False
    bail_timeout = 60

    # Default Authentication File Path
    crasshrc = os.path.expanduser("~") + "/.crasshrc"

    # Get script options - http://www.cyberciti.biz/faq/python-command-line-arguments-argv-example/
    try:
        myopts, args = getopt.getopt(sys.argv[1:],"c:s:t:d:A:U:P:hpwXe")
    except getopt.GetoptError as e:
        print ("\n ERROR: %s" % str(e))
        print_help(2)

    for o, a in myopts:
        if o == '-s':
            sfile=a
            switches = readtxtfile(sfile)

        if o == '-c':
            cfile=a
            commands = readtxtfile(cfile)

        if o == '-t':
            bail_timeout=int(a)

        if o == '-h':
            print("\n Nick\'s Cisco Remote Automation via Secure Shell - Script, or C.R.A.SSH for short! ")
            print_help()

        if o == '-p':
            writeo = False
            printo = True

        if o == '-w':
            writeo = True

        if o == '-X':
          play_safe = False

        if o == '-e':
          enable = True

        if o == '-d':
            delay_command = True
            delay_command_time=int(a)
        
        if o == '-A':
            crasshrc=str(a)

        if o == '-U':
            username=str(a)

        if o == '-P':
            password=str(a)

    # See if we have an Authentication File
    if os.path.isfile(crasshrc) == True:
        try:
            username, password = readauthfile(crasshrc)
        except:
            pass
        
    if sfile == "":
        try:
            iswitch = input("Enter the switch to connect to: ")
            switches.append(iswitch)
        except:
            sys.exit()

    if cfile == "":
        try:
            icommand = input("The switch command you want to run: ")
            commands.append(icommand)
        except:
            sys.exit()

    """
        Check the commands are safe
    """
    if play_safe:
        for command in commands:
            do_no_harm(command)
    else:
        print("\n--\n Do no Harm checking DISABLED! \n--\n")

    """
        Capture Switch log in credentials...
    """

    try: 
        username
    except:
        try:
            username = input("Enter your username: ")
        except:
            sys.exit()

    try:
        password
    except:
        try:
            password = getpass.getpass("Enter your password:")
        except:
            sys.exit()

    if enable:
        try:
            enable_password = getpass.getpass("Enable password:")
        except:
            sys.exit()


    """
        Time estimations for those delaying commands
    """
    if delay_command:
        time_estimate = datetime.timedelta(0,(len(commands) * (len(switches) * 2) * delay_command_time)) + datetime.datetime.now()
        print(" Start Time: %s" % datetime.datetime.now().strftime("%H:%M:%S (%y-%m-%d)"))
        print(" Estimatated Completion Time: %s" % time_estimate.strftime("%H:%M:%S (%y-%m-%d)"))

    """
        Progress calculations - for big jobs only
    """
    if (len(commands) * len(switches)) > 100:
        counter = 0

    """
        Ready to loop thru switches
    """

    for switch in switches:
        
        hostname = connect(switch, username, password, enable)

        # Write the output to a file (optional) - prepare file + filename before CMD loop
        if writeo:
            filetime = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
            filename = hostname + "-" + filetime + ".txt"
            filenames.append(filename)
            f = open(filename,'a')

        # Command Loop
        for cmd in commands:

            # Send the Command
            print("%s: Running: %s" % (hostname, cmd))
            output = send_command(cmd, hostname, bail_timeout)

            # Print the output (optional)
            if printo:
                print(output)
            if writeo:
                f.write(output)

            # delay next command (optional)
            if delay_command:
                time.sleep(delay_command_time)

            # Print progress
            try:
                counter
                if (counter % 10) == 0:
                    completion = ( (float(counter) / ( float(len(commands)) * float(len(switches)))) * 100 )
                    if int(completion) > 9:
                        print("\n  %s%% Complete" % int(completion))
                        if delay_command:
                            time_left = datetime.timedelta(0, (((int(len(commands)) * int(len(switches))) + (len(switches) * 0.5)) - counter)) + datetime.datetime.now()
                            print("  Estimatated Completion Time: %s" % time_left.strftime("%H:%M:%S (%y-%m-%d)"))
                        print(" ")
                counter += 1
            except:
                pass


        # /end Command Loop

        if writeo:
            # Close the File
            f.close()


        # Disconnect from SSH
        disconnect()

        if writeo:
            print("Switch %s done, output: %s" % (switch, filename))
        else:
            print("Switch %s done" % switch)

        # Sleep between SSH connections
        time.sleep(1)

    print("\n")

    print(" ********************************** ")
    if writeo:
        print("  Output files: ")

        for ofile in filenames:
            print("   - %s" % ofile)

        print(" ---------------------------------- ")
    print(" Script FINISHED ! ")
    if delay_command:
        print(" Finish Time: %s" % datetime.datetime.now().strftime("%H:%M:%S (%y-%m-%d)"))
    print(" ********************************** ")

# If run from interpreter, run main code function.
if __name__ == "__main__":
    main()