import os
from getpass import getpass
import socket
import random
import time

class myFTP:
    COMMANDS = {"help": "Print local help information",
                "lcd": "Change local working directory",
                "open": "Connect to remote ftp",
                "quit": "Terminate ftp session and exit",
                "bye": "Terminate ftp session and exit",
                "disconnect": "Terminate ftp session",
                "close": "Terminate ftp session",
                "user": "Send new user information",
                "ls": "List contents of remote directory",
                "cd": "Change remote working directory",
                "pwd": "Print working directory on remote machine",
                "mkdir": "Make directory on the remote machine",
                "rmdir": "Remove directory on the remote machine",
                "type": "Set file transfer type",
                "ascii": "Set ascii transfer type",
                "binary": "Set binary transfer type",
                "get": "Receive file",
                "put": "Send one file",
                "rename": "Rename file",
                "delete": "Delete remote file",
                "quote": "Send arbitrary ftp command"}
    
    TYPES = {"ascii": "A", "binary": "I","image": "I", "tenex": "L 8"}
    
    def __init__(self):
        self.my_ipv4 = socket.gethostbyname(socket.gethostname())
        self.client_socket = None
        self.current_connection = ""
        self.locale_path = os.getcwd()
        self.transfer_type = "ascii"
        
    def help_command(self, specifics:list = []):
        if (specifics == []):
            print("Commands may be abbreviated.  Commands are:\n")
            
            commands = sorted(self.COMMANDS.keys())
            for i in range(len(commands)):
                print(commands[i].ljust(16," "), end="")
                if (i % 5 == 4):
                    print()
            
            print()
            return

        for item in specifics:
            if (item not in self.COMMANDS):
                print(f"Ambiguous help command {item}.")
            
            else:
                command = self.COMMANDS[item]
                print(item.ljust(16," "), command)
            
    def lcd_command(self, path:str = ""):
        
        if (path == ""):
            self.locale_path = os.getcwd()
            print("Local directory now ", self.locale_path)

        elif (path != ""):
            if (os.path.isabs(path)):
                self.locale_path = path
                print("Local directory now ", self.locale_path)

            elif (os.path.isdir(os.path.join(self.locale_path, path))):
                if (path == "."):
                    print("Local directory now ", self.locale_path)

                elif (path == ".."):
                    self.locale_path = os.path.abspath(os.path.join(self.locale_path, os.pardir))
                    print("Local directory now ", self.locale_path)

                elif (os.path.isdir(os.path.join(self.locale_path, path))):
                    self.locale_path = os.path.join(self.locale_path, path)
                    print("Local directory now ", self.locale_path)
                
            elif (os.path.isfile(path)):
                print(f"{path[0]}:Invalid argument")
                
            else:
                print(f"{path}: File not found")
            
    def open_command(self, connection_string:str, port:int = 21):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((connection_string, int(port)))
            self.client_socket.settimeout(10)
            
            res = self.client_socket.recv(1024)
            if (res.decode().startswith("220")):
                if connection_string.startswith("127."):
                    self.my_ipv4 = connection_string
                self.current_connection = connection_string
                
                print(f"Connected to {self.current_connection}")
                self.print_inline(res.decode())
                self.send_and_res("OPTS UTF8 ON")

                user = input(f"User ({self.current_connection}:(none)): ")
                
                res = self.send_and_res(f"USER {user}")

                if (res.startswith("331")):
                    password = getpass("Password: ")
                    
                    res = self.send_and_res(f"PASS {password}")
                    if (res.startswith("230")):
                        return

                print("Login failed.")

        except:
            self.close_connection()
            print(f"Unknown host {connection_string}.")
            
    def user_command(self, username:str, password:str = ""):
        res = self.send_and_res(f"USER {username}")
        if (res.startswith("331")):
            if (password == ""):
                password = (getpass("Password: "))
            
            res = self.send_and_res(f"PASS {password}")
            if (not res.startswith("230")):
                print("Login failed.")
        
        else:
            print("Login failed.")
            
    def ls_command(self, command:str, destination:str = "", local_file:str = ""):
        format_port, port = self.get_port_format()
        res = self.send_and_res(f"PORT {format_port}")
        
        if (res.startswith("200")):
            if (command.startswith("L")):
                res = self.send_and_res(f"LIST {destination}")
            else:
                res = self.send_and_res(f"NLST {destination}")
            
            if (res.startswith("550")):
                return
            
            data_socket = self.init_data_socket(self.my_ipv4, port)
            connection_socket, addr = data_socket.accept()
            
            file_data = b""
            start_time = time.time()
            while True:
                data_received = connection_socket.recv(1024)
                file_data += data_received
                
                if not data_received:
                    end_time = time.time()
                    file_size = len(file_data)
                    break
                
                if (local_file == ""):
                    self.print_inline(data_received.decode())
                else:
                    file_path = os.path.join(self.locale_path, local_file)
                    with open(file_path, 'wb') as file:
                        file.write(file_data)
        
            connection_socket.close()
            data_socket.close()
            
            data = self.client_socket.recv(1024)
            self.print_inline(data.decode())
            
            elapsed_time = end_time - start_time
            self.print_summary(elapsed_time, file_size + 3)
            
    def cd_command(self, path:str):
        self.send_and_res(f"CWD {path}")
        
    def pwd_command(self):
        self.send_and_res("XPWD")
        
    def mkdir_command(self, dir_name:str):
        self.send_and_res(f"XMKD {dir_name}")
        
    def rmdir_command(self, dir_name:str):
        self.send_and_res(f"XRMD {dir_name}")
        
    def type_command(self, type_keyword:str = ""):
        if (type_keyword == ""):
            print(f"Using {self.transfer_type} mode to transfer files.")
        
        elif (type_keyword in self.TYPES.keys()):
            type_value = self.TYPES[type_keyword]
            res = self.send_and_res(f"TYPE {type_value}")
            if (res.startswith("200")):
                self.transfer_type = type_keyword
            
        else:
            print(f"{type_keyword}: unknown mode.")
        
    def get_command(self, remote_file:str, local_file:str = ""):
        port_format, random_port = self.get_port_format()
        res = self.send_and_res(f"PORT {port_format}")

        if (res.startswith("200")):
            res = self.send_and_res(f"RETR {remote_file}")
            if (res.startswith("550")):
                return
            
            data_socket = self.init_data_socket(self.my_ipv4, random_port)
            connection_socket, addr = data_socket.accept()

            if ("/" in local_file):
                local_file = local_file.replace("/", "\\")
            elif (local_file == ""):
                local_file = remote_file.split("/")[-1]

            final_path = os.path.join(self.locale_path, local_file)
            directory = os.path.dirname(final_path)
            if (not os.path.exists(directory)):
                os.makedirs(directory)
                
            file_data = b""
            start_time = time.time()
            while True:
                data_received = connection_socket.recv(1024)
                file_data += data_received
                if not data_received:
                    end_time = time.time()
                    file_size = len(file_data)
                    break
            
            print(self.locale_path)
            print(final_path)
            print(local_file)
            try:
                with open(final_path, 'wb') as file:
                    file.write(file_data)
            except:
                print(f"Error opening local file {local_file}")
                print("> l:Unknown error number")
                return
                
            connection_socket.close()
            data_socket.close()
            
            data = self.client_socket.recv(1024)
            self.print_inline(data.decode())
            
            elapsed_time = end_time - start_time
            self.print_summary(elapsed_time, file_size)
        
    def put_command(self, local_file:str, remote_file:str = ""):
        if ("/" in local_file):
            local_file = local_file.replace("/", "\\")
        if (remote_file == ""):
            remote_file = local_file.split("\\")[-1]
        local_file_path = os.path.join(self.locale_path, local_file)

        if not os.path.exists(local_file_path):
            print(f"{local_file}: File not found")
            return
            
        port_format, random_port = self.get_port_format()
        res = self.send_and_res(f"PORT {port_format}")

        if (res.startswith("200")):
            res = self.send_and_res(f"STOR {remote_file}")
            if (res.startswith("550")):
                return
            
            data_socket = self.init_data_socket(self.my_ipv4, random_port)
            connection_socket, addr = data_socket.accept()
            
            with open(local_file_path, "rb") as file:
                file_data = b""
                start_time = time.time()
                while True:
                    chunk = file.read(4096)
                    file_data += chunk
                    if not chunk:
                        end_time = time.time()
                        file_size = len(file_data)
                        break
                    connection_socket.send(chunk)
                
            connection_socket.close()
            data_socket.close()
                
            data = self.client_socket.recv(1024)
            self.print_inline(data.decode())
            
            elapsed_time = end_time - start_time
            self.print_summary(elapsed_time, file_size + 3)
        
    def rename_command(self, from_name:str, to_name:str):
        res = self.send_and_res(f"RNFR {from_name}")
        
        if (res.startswith("350")):
            self.send_and_res(f"RNTO {to_name}")
    
    def delete_command(self, remote_file:str):
        self.send_and_res(f"DELE {remote_file}")
    
    def quote_command(self, quote):
        self.send_and_res(f"{quote}")
    
    def close_command(self):
        self.send_and_res("QUIT")
        self.reset_connection()
    
    def is_socket_available(self):
        return (self.client_socket and self.client_socket.fileno() != -1)
    
    def print_inline(self, mes:str):
        print(mes[:-2:])

    def send_and_res(self, mes:str, print_res:bool = True):
        self.client_socket.send(f"{mes}\r\n".encode("utf-8"))
        res = self.client_socket.recv(1024).decode()
        
        if (print_res == True):
            self.print_inline(res)
            
        return res

    def init_data_socket(self, ip:str, port:int):
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.settimeout(10)
        data_socket.bind((ip, port))
        data_socket.listen(10)
        
        return data_socket

    def split_two_comma(self, num:int):
        return str(num // 256) + "," + str(num % 256)
    
    def get_port_format(self):
        rand_port = random.randint(1024, 65535)
        port_format = (self.my_ipv4 + "," + 
            self.split_two_comma(rand_port)).replace(".",",")
        
        return port_format, rand_port
    
    def print_summary(self, elapsed_time:time, file_size:int):
        if (elapsed_time <= 0):
            elapsed_time = 0.0000001
        rate = (file_size / 1000) / elapsed_time
        if (rate > file_size):
            rate = file_size
        print(f"ftp: {file_size} bytes received in {elapsed_time:.2f}Seconds {rate:.2f}Kbytes/sec.")

    def reset_connection(self):
        self.my_ipv4 = socket.gethostbyname(socket.gethostname())
        self.client_socket.close()
        self.current_connection = ""