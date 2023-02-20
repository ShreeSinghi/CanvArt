#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 12:57:44 2023

@author: shree
"""
import struct
import cv2
import socket
import pickle

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host_ip = socket.gethostbyname(socket.gethostname())
PORT = 11027
print('HOST IP and PORT:', host_ip, PORT)

socket_address = (host_ip,PORT)
server.bind(socket_address)
server.listen(5)

print('Listening')

try:
    while True:
        client, addr = server.accept()
        print('Connection from:',addr)
        if client:
            video = cv2.VideoCapture(0)
            while(video.isOpened()):
                showing, frame = video.read()
                pickle_data = pickle.dumps(frame)
                
                # size of pickle is stored in a long long int (represented by Q)
                message = struct.pack("Q", len(pickle_data)) + pickle_data
                client.sendall(message)
                cv2.imshow('server',frame)
                cv2.waitKey(10)
except KeyboardInterrupt:
    client.close()
    video.release()