#!/usr/bin/env python

###AVAYA TELNETTING###


#Importing the necessary modules
import telnetlib
import subprocess
import threading
import os.path
import logging
import time
import sys
import re


#Checking IP address validity
def IpIsValidReach():
    check = False
    global ip_list
    
    while True:
        #Prompting user for input
        ip_file = raw_input("Enter IP file name and extension: ")
                
        #Changing exception message
        try:
            #Open user selected file for reading (IP addresses file)
            selected_ip_file = open(ip_file, 'r')
            
            #Starting from the beginning of the file
            selected_ip_file.seek(0)
            
            #Reading each line (IP address) in the file
            ip_list = selected_ip_file.readlines()
            
            #Closing the file
            selected_ip_file.close()
            
        except IOError:
            print "\nFile %s does not exist! Please check and try again!\n" % ip_file
            
        #Checking octets            
        for ip in ip_list:
            a = ip.split('.')
            
            if (len(a) == 4) and (1 <= int(a[0]) <= 223) and (int(a[0]) != 127) and (int(a[0]) != 169 or int(a[1]) != 254) and (0 <= int(a[1]) <= 255 and 0 <= int(a[2]) <= 255 and 0 <= int(a[3]) <= 255):
                check = True
                break
                 
            else:
                print '\n* There was an INVALID IP address! Please check and try again!\n'
                check = False
                continue
            
        #Evaluating the 'check' flag    
        if check == False:
            continue
        
        elif check == True:
            break
 
    #Checking IP reachability
    print "\nChecking IP reachability...\n"
    
    check2 = False
    
    while True:
        for ip in ip_list:
            ping_reply = subprocess.call(['ping', '-c', '3', '-w', '3', '-q', '-n', ip], stdout = subprocess.PIPE)
            
            if ping_reply == 0:
                check2 = True
                continue
            
            elif ping_reply == 2:
                print "\nNo response from device %s." % ip
                check2 = False
                break
            
            else:
                print "\nPing to the following device has FAILED:", ip
                check2 = False
                break
            
        #Evaluating the 'check' flag 
        if check2 == False:
            print "Please re-check IP address list or device.\n"
            IpIsValidReach()
        
        elif check2 == True:
            print '\nAll devices are reachable. Waiting for command file...\n'
            break
    
#Checking command file validity
def CommandFileExists():
    global cmd_file
    
    while True:
        cmd_file = raw_input("Enter command file name and extension: ")
        
        #Changing exception message
        if os.path.isfile(cmd_file) == True:
            print "\nCommands file was found.\n"
            break
        
        else:
            print "\nFile %s does not exist! Please check and try again!\n" % cmd_file
            continue



#Open telnet connection to devices and send "show" commands + save to NVRAM option
def ReadConfig(ip, username, password, show_command, to_file = True, to_screen = False):
    #Change exception message
    try:
        #Specify the Telnet port (default is 23, anyway)
        port = 23
        
        #Specify the connection timeout in seconds for blocking operations, like the connection attempt
        connection_timeout = 5
        
        #Specify a timeout in seconds. Read until the string is found or until the timout has passed
        reading_timeout = 5
        
        ###DEBUG CODE
        #print ip
        #print username
        #print password
        
        #Logging into device
        connection = telnetlib.Telnet(ip, port, connection_timeout)
        time.sleep(1)
        
        #Sending CTRL+Y to get the prompt
        connection.write("\x19")
        time.sleep(1)
        
        #Waiting to be asked for an username
        router_output = connection.read_until("Enter Username:", reading_timeout)
        #Enter the username when asked and a "\n" for Enter
        connection.write(username + "\n")
        time.sleep(1)
        
        #Waiting to be asked for a password
        router_output = connection.read_until("Enter Password:", reading_timeout)
        #Enter the password when asked and a "\n" for Enter
        connection.write(password + "\n")
        time.sleep(1)
                
        #Setting terminal length for the entire output - disabling pagination
        #Useful for reading output
        connection.write("terminal length 0\n")
        time.sleep(1)
        
        #Setting terminal width for broader output
        #Useful for reading output
        connection.write("terminal width 132\n")
        time.sleep(1)
        
        #Sending "show" command
        connection.write("\n")
        connection.write(show_command + "\n")
        time.sleep(25)   #Setting 25 seconds delay for longer outputs, like in the case of "show tech"
        
        #Reading command output
        router_output = connection.read_very_eager()
        
        ###DEBUG CODE
        #print to_file
        #print to_screen
        #print router_output
        
        #Getting device hostname from output, for naming the file to which to save the output
        hostname_regex = re.search(r"(.+?)#show ", router_output)
        hostname = hostname_regex.group(1)
        
        ###DEBUG CODE
        #print hostname_regex
        #print hostname
        
        #Formatting output to eliminate lines containing the prompt - splitting the string by '\n'
        #Each time, the first 5 lines (indexes 0-4) are the ones we don't want, so they should be eliminated
        #Also, the prompt is returned once again at the end of the output, so we should eliminate that, too
        #This means eliminating the final line as well (index -1)
        nice_router_output = '\n'.join(router_output.split('\n')[5:-1])
        #print nice_router_output
        
        #Handling invalid commands by searching the output for this string: "'^' marker"
        if "'^' marker" in nice_router_output:
            print "\nInvalid command sent to the device. Please try again.\n"
            sys.exit() 
        
        #Handling the to_file parameter
        if to_file == True:
            with open(hostname + '_' + show_command.replace(' ', '_') + '.txt', 'w+') as f:
                f.write(nice_router_output)
            print "\nOutput was written to %s." % (hostname + '_' + show_command.replace(' ', '_') + '.txt')
            print "\n"
        
        elif to_file == False:
            pass
        
        #Handling the to_screen parameter
        if to_screen == True:
            print nice_router_output
            
        elif to_screen == False:
            pass
        
        ##### resolve with first two functions in file
        ##### resolve with sendmultidev()
        
        #Closing the connection
        connection.close()
        
    except IOError:
        print "\nInput parameter error! Please check destination IP, username and password.\n"
        sys.exit()
        
    except AttributeError:
        print "\nInput parameter error! Please check destination IP, username and password.\n"
        sys.exit()
        
    except KeyboardInterrupt:
        print "\nProgram aborted by user. Exiting...\n"
        sys.exit()



#Open telnet connection to devices and send config commands + save to NVRAM option
def SendConfig(ip, cmd_file, username, password, save_config = True):
    #Change exception message
    try:
        #Specify the Telnet port (default is 23, anyway)
        port = 23
        
        #Specify the connection timeout in seconds for blocking operations, like the connection attempt
        connection_timeout = 5
        
        #Specify a timeout in seconds. Read until the string is found or until the timout has passed
        reading_timeout = 5
        
        ###DEBUG CODE
        #print ip
        #print username
        #print password
        
        #Logging into device
        connection = telnetlib.Telnet(ip, port, connection_timeout)
        time.sleep(1)
        
        #Sending CTRL+Y to get the prompt
        connection.write("\x19")
        time.sleep(1)
        
        #Waiting to be asked for an username
        router_output = connection.read_until("Enter Username:", reading_timeout)
        #Enter the username when asked and a "\n" for Enter
        connection.write(username + "\n")
        time.sleep(1)
        
        #Waiting to be asked for a password
        router_output = connection.read_until("Enter Password:", reading_timeout)
        #Enter the password when asked and a "\n" for Enter
        connection.write(password + "\n")
        time.sleep(1)
                
        #Verifying if the credentials are correct and properly sent to the device
        router_output = connection.read_very_eager()
        
        if "Incorrect Credentials" in router_output:
            print "\nIncorrect Credentials. Please check username and password.\n"
            sys.exit()
            
        elif "Telnet Login Timer Expired" in router_output:
            print "\nTelnet Login Timer Expired. Please check the connection.\n"
            sys.exit()
            
        else:
            pass
                
        #If credentials were correct -> Entering global config mode
        connection.write("\n")
        connection.write("configure terminal\n")
        time.sleep(1)
        
        #Checking if the command(s) file exists (in the current directory when you enter just the file name, without a full path)
        if os.path.isfile(cmd_file) == True:
             #Open user selected file for reading
            selected_cmd_file = open(cmd_file, 'r')
            
            #Starting from the beginning of the file
            selected_cmd_file.seek(0)
        
            #Writing each line in the file to the device
            for each_line in selected_cmd_file.readlines():
                #print each_line
                connection.write(each_line + '\n')
                time.sleep(1)
    
            #Closing the file
            selected_cmd_file.close()
        
        else:
            print "\nFile %s does not exist! Please check filename or path and try again.\n" % cmd_file
            sys.exit()

        ###DEBUG CODE
        #Test for reading command output
        #router_output = connection.read_very_eager()
        #print router_output
        
        if save_config == True:
            #Saving the config to NVRAM
            connection.write("\n")
            connection.write("copy config nvram\n")
            time.sleep(5)
            print "\nConfiguration was saved to NVRAM.\n"
        
        elif save_config == False:
            print "\nConfiguration was not saved.\n"
            pass
        
        #Closing the connection
        connection.close()
        
    except IOError:
        print "\nInput parameter error! Please check destination IP, command file name, username and password.\n"
        
    except KeyboardInterrupt:
        print "\n\nProgram aborted by user. Exiting...\n"
        sys.exit()

  
#Creating threads
def SendConfigToMultiDev(username, password, save_config = True):
    IpIsValidReach()
    CommandFileExists()
    
    threads = []
    for ip in ip_list:
        th = threading.Thread(target = SendConfig, args = (ip, cmd_file, username, password, save_config))   #'args' is a tuple
        th.start()
        threads.append(th)
        
    for th in threads:
        th.join()



#This code will NOT be executed at import
if __name__ == "__main__":
    
    #Change exception message
    try:
        #Calling IP validity function    
        IpIsValidReach()
        
    except KeyboardInterrupt:
        print "\n\nProgram aborted by user. Exiting...\n"
        sys.exit()
    
    #Change exception message
    try:
        #Calling command file validity function
        CommandFileExists()
        
    except KeyboardInterrupt:
        print "\n\nProgram aborted by user. Exiting...\n"
        sys.exit()
        
    #Calling threads creation function
    SendConfigToMultiDev()



#End of program