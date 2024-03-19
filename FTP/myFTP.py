import os
from getpass import getpass
from socket_handle import *
import random

client_socket = None
current_connect = ""
locale_path = os.getcwd()
my_ipv4 = socket.gethostbyname(socket.gethostname())

while (True):
    rand = int(random.random() * 9999 + 20000)
    # use random to select port because my pc got weird on old active port even kill session
    # could bring this better port selection
    ip_comma = (my_ipv4 + "." + split_two_comma(rand)).replace(".",",")
    
    inp = input("ftp> ").strip()
    args = inp.split()
    command = args[0]
    
    if (command == "quit" or command == "bye"):
        if (is_socket_available(client_socket)):
            send_and_res(client_socket, "QUIT")

            client_socket.close()
            break
        
        print()
        break

    elif (command == "disconnect" or command == "close"):
        if (not is_socket_available(client_socket)):
            print("Not connected.")
            continue
        
        if (is_socket_available(client_socket)):
            send_and_res(client_socket, "QUIT")

            client_socket.close()
            current_connect = ""
            
        else:
            print("Not connected.")
    
    elif (command == "open"):
        if (is_socket_available(client_socket)):
            print(f"Already connected to {current_connect}, use disconnect first.")
            continue
        
        elif (len(args) < 2):
            args.append(input("To "))
            
            if (args[1] == ""):
                print("Usage: open host name [port]")
                continue

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((args[1], 21))
            client_socket.settimeout(10)
            
            res = client_socket.recv(1024)
            if (res.decode().startswith("220")):
                current_connect = args[1]
                
                print(f"Connected to {current_connect}")
                print_inline(res.decode())
                send_and_res(client_socket, "OPTS UTF8 ON")

                user = input(f"User ({current_connect}:(none)): ")
                
                res = send_and_res(client_socket, f"USER {user}")

                if (res.startswith("331")):
                    password = getpass("Password: ")
                    
                    res = send_and_res(client_socket, f"PASS {password}")
                    if (res.startswith("230")):
                        continue

                print("Login failed.")

        except:
            print(f"Unknown host {args[1]}.")
        
    elif (command == "user"):
        if (not is_socket_available(client_socket)):
            print("Not connected.")
            continue
        
        if (len(args) < 2):
            args.append(input("Username "))

            if (args[1] == ""):
                print("Usage: user username [password] [account]")
                continue

        send_and_res(client_socket, f"USER {args[1]}")

        if (len(args) < 3):
            args.append(getpass("Password: "))
            
        res = send_and_res(client_socket, f"PASS {args[2]}")
        if (not res.startswith("230")):
            print("Login failed.")
    
    elif (command == "lcd"):
        if (len(args) < 2):
            locale_path = os.getcwd()
            print("Local directory now ", locale_path)

        elif (len(args) == 2):
            if (os.path.isabs(args[1])):
                locale_path = args[1]
                print("Local directory now ", locale_path)
                
            elif (os.path.isdir(args[1])):
                locale_path = os.path.join(locale_path, args[1])
                print("Local directory now ", locale_path)
                
            elif (os.path.isfile(args[1])):
                print(f"{args[1][0]}:Invalid argument")
                
            else:
                print(f"{args[1]}: File not found")

        else:
            print("lcd local directory.")
    
    elif (command.lower() == "ls"):
        if (not is_socket_available(client_socket)):
            print("Not connected.")
            continue

        res = send_and_res(client_socket, f"PORT {ip_comma}")
        
        if (res.startswith("200")):
            data_socket = init_data_socket(my_ipv4, rand)
            conn, addr = data_socket.accept()
            
            if (command.startswith("L")):
                send_and_res(client_socket, "LIST")
            else:
                send_and_res(client_socket, "NLST")
            
            while True:
                data_received = conn.recv(1024)
                
                if not data_received:
                    break
                
                print_inline(data_received.decode())
        
            conn.close()
            data_socket.close()
            
            data = client_socket.recv(1024)
            print_inline(data.decode())

    elif (command == "get"):
        if (not is_socket_available(client_socket)):
            print("Not connected.")
            continue
        
        if (len(args) < 2):
            args.append(input("Remote file "))
            
            if (args[1] == ""):
                print("Remote file get [ local-file ].")
                continue
            
            else:
                args.append(input("Local file "))
            
        res = send_and_res(client_socket, f"PORT {ip_comma}")

        if (res.startswith("200")):
            data_socket = init_data_socket(my_ipv4, rand)
            conn, addr = data_socket.accept()
            
            send_and_res(client_socket, f"RETR {args[1]}")

            if (args[2] != ""):
                args[1] = args[2]

            final_path = os.path.join(locale_path, args[1])
            while True:
                data_received = conn.recv(1024)
                if not data_received:
                    break
                
                with open(final_path, 'wb') as file:
                        file.write(data_received)

                print("File downloaded successfully.")
                
            conn.close()
            data_socket.close()
            
            data = client_socket.recv(1024)
            print_inline(data.decode())

        else:
            print_inline(data.decode())
    
    elif (command == "put"):
        if (not is_socket_available(client_socket)):
            print("Not connected.")
            continue
        
        if (len(args) < 2):
            args.append(input("Local file "))
            
            if (args[2] == ""):
                print("Local file put: remote file.")
                continue
            
        res = send_and_res(client_socket, f"PORT {ip_comma}")

        if (res.startswith("200")):
            data_socket = init_data_socket(my_ipv4, rand)
            conn, addr = data_socket.accept()
            
            send_and_res(client_socket, f"STOR {args[1]}")
    
    elif (command == "rename"):
        if (not is_socket_available(client_socket)):
            print("Not connected.")
            continue
        
        if (len(args) < 2):
            args.append(input("From name "))
            
            if (args[1] == ""):
                print("rename from-name to-name.")
                continue
        
        if (len(args) < 3):
            args.append(input("To name "))
            
            if (args[2] == ""):
                print("rename from-name to-name.")
                continue
            
        res = send_and_res(client_socket, f"RNFR {args[1]}")
        
        if (res.startswith("350")):
            send_and_res(client_socket, f"RNTO {args[2]}")
            
    elif (command == "delete"):
        send_and_res(client_socket, f"DELE {args[1]}")
                    
    elif (command == "ascii"):
        send_and_res(client_socket, "TYPE A")
        
    elif (command == "binary"):
        send_and_res(client_socket, "TYPE I")
        
    elif (command == "cd"):
        send_and_res(client_socket, f"CWD {args[1]}")
        
    elif (command == "pwd"):
        send_and_res(client_socket, "XPWD")