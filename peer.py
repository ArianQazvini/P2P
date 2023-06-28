import json
import random
import socket
import requests
import threading
import tkinter as tk
import numpy as np
from tkinter import messagebox
from tkinter.simpledialog import askinteger
from PIL import Image
import pickle
import zlib
# def udp_send_connection_ack(sock,destIp,destPort):
#     msg = input(f"Enter Message to  {destIp}:{destPort}")
#     sock.sendto(msg.encode('utf-8'), (destIp, destPort))
#     print(f"Sent to receiver: {msg}")
def tcp_connection_listen(tcp_listen_port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(("127.0.0.1",tcp_listen_port))
    sock.listen()
    # is_tcp_listening=True
    client_socket, client_address = sock.accept()
    file_address = f"text_{tcp_listen_port}.txt"
    with open('./downloaded/' + file_address, 'wb') as file:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file.write(data)
    messagebox.showinfo("Download Completed",f"Text file downloaded from {client_address} and saved at {file_address}")
    sock.close()

def send_text(tcp_port):
    sock =  socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect(("127.0.0.1",tcp_port))
    file_address = file_address_input.get(1.0,"end-1c")
    print(file_address)
    try:
        with open('./files/' + file_address, 'rb') as file:
            file_data = file.read()
        sock.sendall(file_data)
        messagebox.showinfo("Response","Text file Sent Successfully.")
        sock.close()
    except FileNotFoundError:
        messagebox.showinfo("Response", "Text file not found.")
        sock.close()

def image_connection_listen(ip, image_listen_port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind((ip,image_listen_port))
    dim, address= sock.recvfrom(1024)
    dim = dim.decode()
    print(dim)
    rows = int(dim.split("/")[0])
    columns = int(dim.split("/")[1])

    # checksum_bytes,_ = sock.recvfrom(4096)
    # recieved_checksum = int.from_bytes(checksum_bytes, byteorder='big')
    rows_arr = []
    while True:
        data, address = sock.recvfrom(1024)
        if data==b'Finished':
            break
        rows_arr.append(data)
    sock.close()
    image_data = b''.join(rows_arr)
    # calculated_checksum = zlib.crc32(image_data)
    # if(calculated_checksum==recieved_checksum):
    #     print("Equal checksum")
    image_array = np.frombuffer(image_data, dtype=np.uint8).reshape((rows, columns,-1))
    recieved_image = Image.fromarray(image_array)
    recieved_image.save(f"./downloaded/downloaded{image_listen_port}.jpeg")
    print("Done")
    sock.close()
def send_image(image_port):
    sock =  socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    file_address = file_address_input.get(1.0, "end-1c")
    try:
        image = Image.open('./files/' +file_address)
        image_array = np.asarray(image)
        rows, columns, channels = image_array.shape
        print(image_array.shape)

        dim= f"{rows}/{columns}"
        sock.sendto(dim.encode(), ("127.0.0.1", image_port))

        image_data = image.tobytes()
        # checksum = zlib.crc32(image_data)
        # checksum_bytes = checksum.to_bytes(4, byteorder='big')
        # sock.sendto(checksum_bytes, ("127.0.0.1", image_port))

        print(len(image_data))
        print("-----------------------")
        packet_size = 1024
        total_packets = (len(image_data) + packet_size - 1) // packet_size
        for i in range(total_packets):
            if i == total_packets - 1:
                chunk = image_data[i * packet_size:]
            else:
                chunk = image_data[i * packet_size: (i + 1) * packet_size]
            sock.sendto(chunk, ("127.0.0.1", image_port))
        sock.sendto(b'Finished', (("127.0.0.1", image_port)))
        sock.close()
        print("Image Sent Successfully.")
    except FileNotFoundError:
        messagebox.showinfo("Image not found")
        sock.close()

def udp_connection_listen(ip,udp_listen_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, udp_listen_port))
    print(f"Peer listening on UDP: {ip}:{udp_listen_port}")
    while True:
        data, sender_address = sock.recvfrom(2048)
        data = data.decode('utf-8')
        msg = data.split('/')[0]
        msg_type = data.split('/')[1]
        sender_ip = "127.0.0.1"
        print(data.split('/'))
        sender_port = int(data.split('/')[2])
        tcp_port = int(data.split('/')[3])
        image_port = int(data.split('/')[4])
        if(msg_type=="Connection-Request"):
            res = messagebox.askquestion("Message Request",f"{msg} from {sender_ip}/{sender_port}")
            if(res=='yes'):
                sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                msg = f"Yes/Connection-Request-Accept/{udp_listen_port}/{tcp_port}/{image_port}"
                sock2.sendto(msg.encode('utf-8'), (sender_ip,sender_port))
                sock2.close()
            else:
                sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                msg = f"No/Connection-Request-Decline/{udp_listen_port}/{tcp_port}/{image_port}"
                sock2.sendto(msg.encode('utf-8'), (sender_ip,sender_port))
                sock2.close()
        elif(msg_type=="Connection-Request-Accept"):
            if(messageType=='Text'):
                # global tcp_port
                # tcp_port = int(tcp_port_input.get(1.0,"end-1c"))
                # print(tcp_port)
                sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                msg = f"Open TCP connection on port {tcp_port}/TCP-Connection-Open-Request/{udp_listen_port}/{tcp_port}/{image_port}"
                sock2.sendto(msg.encode('utf-8'), (sender_ip,sender_port))
                sock2.close()
            else:
                sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                msg = f"Open UDP connection on port {image_port}/UDP-Connection-Open-Request/{udp_listen_port}/{tcp_port}/{image_port}"
                sock2.sendto(msg.encode('utf-8'), (sender_ip,sender_port))
                sock2.close()
        elif(msg_type=="TCP-Connection-Open-Request"):
            # global is_tcp_listening
            # is_tcp_listening=False
            # tcp_port = int(data.split('/')[3])
            threading.Thread(target=tcp_connection_listen,args=(tcp_port,)).start()
            # while(is_tcp_listening==False):
            #     if(is_tcp_listening==True):
            #         break
            print("TCP socket created")
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            msg = f"tcp connection opened/TCP-Connection-Open-Request-Done/{udp_listen_port}/{tcp_port}/{image_port}"
            sock2.sendto(msg.encode('utf-8'), (sender_ip,sender_port))
            sock2.close()

        elif(msg_type=="TCP-Connection-Open-Request-Done"):
            # tcp_port = data.split('/')[3]
            threading.Thread(target=send_text,args=(tcp_port,)).start()

        elif(msg_type=="UDP-Connection-Open-Request"):

            threading.Thread(target=image_connection_listen, args=("127.0.0.1",image_port,)).start()
            print("UDP socket created")
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            msg = f"udp connection opened/UDP-Connection-Open-Request-Done/{udp_listen_port}/{tcp_port}/{image_port}"
            sock2.sendto(msg.encode('utf-8'), (sender_ip,sender_port))

        elif(msg_type=="UDP-Connection-Open-Request-Done"):
            threading.Thread(target=send_image, args=(image_port,)).start()


def register():
    global username
    global udp_port
    username = username_input.get(1.0,"end-1c")
    udp_port = udp_port_input.get(1.0,"end-1c")
    host = socket.gethostbyname(socket.gethostname())
    threading.Thread(target=udp_connection_listen,args=("127.0.0.1",int(udp_port),)).start()
    data = {
            "username": username,
            "address": host+"/"+str(udp_port)

        }
    res = requests.post('http://127.0.0.1:8000/register',json=data)
    res_dict = json.loads(res.text)
    messagebox.showinfo("Respone",res_dict["message"])
    # print(res_dict["message"])

def get_all():
    res = requests.get('http://127.0.0.1:8000/getAll')
    res_dict = json.loads(res.text)
    messagebox.showinfo("Respone", res_dict)
    # print(res_dict)
def get_destination():
    destination_username = get_destination_input.get(1.0,"end-1c")
    res = requests.get('http://127.0.0.1:8000/get'+'?'+destination_username)
    res_dict = res.json()
    print(res_dict)
    dest_ip = res_dict['address'].split('/')[0]
    dest_port=res_dict['address'].split('/')[1]
    messagebox.showinfo("Respone",str(dest_ip)+"/"+str(dest_port))
def send_connection_request():
    tcp_port = int(tcp_port_input.get(1.0, "end-1c"))
    image_port=int(image_port_input.get(1.0, "end-1c"))
    dest_address= destination_address_input.get(1.0,"end-1c")
    destIp = dest_address.split('/')[0]
    destPort = dest_address.split('/')[1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = f"Do you accept connection request?/Connection-Request/{udp_port}/{tcp_port}/{image_port}"
    sock.sendto(msg.encode('utf-8'), (destIp, int(destPort)))
    sock.close()
    global messageType
    messageType= value_inside.get()

def graphic():

    frame = tk.Tk()
    frame.title("Peer")
    frame.configure(background="#00aff0")
    frame.geometry("500x750")
    username_label = tk.Label(frame, text="Enter Username:")
    username_label.pack(pady=10)

    global username_input
    global udp_port_input
    username_input = tk.Text(frame,height=1,width=20)
    username_input.pack()

    udp_label = tk.Label(frame, text="Enter UDP listen port:")
    udp_label.pack(pady=10)
    udp_port_input = tk.Text(frame,height=1,width=20)
    udp_port_input.pack()


    reg_button = tk.Button(frame, text="Register", command=register)
    reg_button.pack(pady=10)

    get_all_button = tk.Button(frame, text="Get All", command=get_all)
    get_all_button.pack(pady=10)

    get_label = tk.Label(frame,text="Get Target internet address:")
    get_label.pack(pady=10)

    global get_destination_input
    get_destination_input = tk.Text(frame,height=1,width=20)
    get_destination_input.pack()

    get_button = tk.Button(frame,text="Get",command=get_destination)
    get_button.pack(pady=10)

    global value_inside
    options= ["Text","Image"]
    value_inside = tk.StringVar(frame)
    value_inside.set("Select an Option")
    question_menu = tk.OptionMenu(frame, value_inside, *options)
    question_menu.pack()
    dest_label = tk.Label(frame,text="Destination Address:")
    dest_label.pack(pady=10)
    global destination_address_input
    destination_address_input = tk.Text(frame,height=1,width=20)
    destination_address_input.pack()
    file_label = tk.Label(frame,text="File Address:")
    file_label.pack(pady=10)
    global file_address_input
    file_address_input = tk.Text(frame,height=1,width=20)
    file_address_input.pack()
    tcp_port_label = tk.Label(frame,text="TCP port for text :")
    tcp_port_label.pack(pady=10)
    global tcp_port_input
    tcp_port_input = tk.Text(frame,height=1,width=20)
    tcp_port_input.pack()
    image_port_label = tk.Label(frame,text="UDP port for image :")
    image_port_label.pack(pady=10)
    global image_port_input
    image_port_input = tk.Text(frame,height=1,width=20)
    image_port_input.pack()
    send_request_button = tk.Button(frame,text="Request",command=send_connection_request)
    send_request_button.pack(pady=10)
    frame.mainloop()




graphic()
# try:
#     image = Image.open('./files/' + "fox.jpg")
#     image_rgp = image.convert("RGB")
#     image_array = np.array(image_rgp)
#     height,width,channels = image_array.shape
#     for i in range(height):
#         image_temp = []
#         for j in range(width):
#             image_temp.append((image_array[i][j][0],image_array[i][j][1],image_array[i][j][2]))
#         print(image_temp)
#         print("------------------")
# except FileNotFoundError:
#     print("Invalid image file path!")