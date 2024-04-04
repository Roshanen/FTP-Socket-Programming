from classFTP import myFTP

ftp = myFTP()

while(True):
    inp = input("ftp> ").strip()
    args = inp.split()
    
    if (len(args) == 0):
        continue
    command = args[0]
    
    if (command.lower() not in ftp.COMMANDS.keys()):
        print("Invalid command.")
        continue
    
    elif (command.lower() == "help"):
        command_list = args[1::]
        ftp.help_command(command_list)
        
    elif (command.lower() == "lcd"):
        if (len(args) > 2):
            print("lcd local directory.")
            continue
        
        path = args[1] if (len(args) > 1) else ""
        ftp.lcd_command(path)

    
    elif (command.lower() == "open"):
        if (ftp.is_socket_available()):
            print(f"Already connected to {ftp.current_connection}, use disconnect first.")
            continue
        
        if (len(args) > 3):
            print("Usage: open host name [port]")
            continue
        elif (len(args) < 2):
            args.append(input("To "))
            if (args[1] == ""):
                print("Usage: open host name [port]")
                continue

        connection_string = args[1]
        port = 21 if len(args) < 3 else args[2]
            
        print(connection_string, port)
        
        ftp.open_command(connection_string, port)
    
    elif (command.lower() == "quit" or command == "bye"):
        if (not ftp.is_socket_available()):
            print()
            break
        
        ftp.close_command()
        break
    
    elif (not ftp.is_socket_available()):
            print("Not connected.")
            continue
    
    elif (command.lower() == "disconnect" or command == "close"):
        ftp.close_command()
        
    elif (command.lower() == "user"):
        if (len(args) > 3):
            print("Usage: user username [password] [account]")
            continue
        
        if (len(args) < 2):
            args.append(input("Username "))

            if (args[1] == ""):
                print("Usage: user username [password] [account]")
                continue
        
        username = args[1]
        password = args[2] if (len(args) > 2) else ""
        ftp.user_command(username, password)
        
    elif (command.lower() == "ls"):
        if (len(args) > 3):
            print("Usage: ls remote directory local file.")
            continue

        destination = args[1] if (len(args) > 1) else ""
        local_file = args[2] if (len(args) > 2) else ""
        
        ftp.ls_command(command, destination, local_file)
        
    elif (command.lower() == "cd"):
        if (len(args) < 2):
            args.append(input("Remote directory "))
            if (args[1] == ""):
                print("cd remote directory.")
                continue
        
        path = args[1]
        ftp.cd_command(path)
        
    elif (command.lower() == "pwd"):
        ftp.pwd_command()
        
    elif (command.lower() == "mkdir"):
        if (len(args) < 2):
            args.append(input("Directory name "))
            
            if (args[1] == ""):
                print("mkdir directory-name")
                continue
        
        dir_name = args[1]
        ftp.mkdir_command(dir_name)
        
    elif (command.lower() == "rmdir"):
        if (len(args) < 2):
            args.append(input("Directory name "))
            
            if (args[1] == ""):
                print("rmdir directory-name")
                continue
            
        dir_name = args[1]
        ftp.rmdir_command(dir_name)
        
    elif (command.lower() == "type"):
        if (len(args) > 2):
            print("Usage: type [ ascii | binary | image | tenex ]")
            continue

        type_keyword = args[1] if (len(args) > 1) else ""

        ftp.type_command(type_keyword)
        
    elif (command.lower() == "ascii"):
        ftp.type_command("ascii")
        
    elif (command.lower() == "binary"):
        ftp.type_command("binary")
        
    elif (command.lower() == "get"):
        if (len(args) < 2):
            args.append(input("Remote file "))
            
            if (args[1] == ""):
                print("Remote file get [ local-file ].")
                continue
            
            else:
                args.append(input("Local file "))

        remote_file = args[1]
        local_file = args[2] if (len(args) > 2) else ""
        
        ftp.get_command(remote_file, local_file)
        
    elif (command.lower() == "put"):
        if (len(args) < 2):
            args.append(input("Local file "))
            if (args[1] == ""):
                print("Local file put: remote file.")
                continue

            args.append(input("Remote file "))
            
        if (len(args) < 3):
            args.append("")
            
        local_file = args[1]
        remote_file = args[2]
        
        ftp.put_command(local_file, remote_file)
        
    elif (command.lower() == "rename"):
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
        
        from_name = args[1]
        to_name = args[2]
        ftp.rename_command(from_name, to_name)
        
    elif (command.lower() == "delete"):
        if (len(args) < 2):
            args.append(input("Remote file "))
            if (args[1] == ""):
                print("delete remote file.")
                continue
        
        remote_file = args[1]
        ftp.delete_command(remote_file)

    elif (command.lower() == "quote"):
        inp = inp[6::]
        if (inp == ""):
            inp = input("Command line to send ")
            
            if (inp == ""):
                print("Usage: quote line to send.")
                continue
            
        ftp.quote_command(inp)