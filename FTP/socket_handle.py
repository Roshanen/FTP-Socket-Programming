import socket

def is_socket_available(socket):
    return (socket and socket.fileno() != -1)

def print_inline(mes):
    print(mes[:-2:])

def send_and_res(socket, mes, print_res = True):
    socket.send(f"{mes}\r\n".encode("utf-8"))
    res = socket.recv(1024).decode()
    
    if (print_res == True):
        print_inline(res)
        
    return res

def init_data_socket(ip, port):
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((ip, port))
    data_socket.listen(10)
    
    return data_socket

def split_two_comma(num):
    return str(num // 256) + "," + str(num % 256)