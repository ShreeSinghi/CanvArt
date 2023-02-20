#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 14:14:07 2023

@author: shree
"""

import socket
import cv2
import pickle
import struct


client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = '127.0.1.1'
PORT = 11027
client.connect((host_ip, PORT)) 

data = b""  # creates an empty data packet

HEADERSIZE = struct.calcsize("Q")

while True:
    # first we receive the header (size of the pickle file)
    while len(data) < HEADERSIZE:
        # the smaller the size of datapacket, the longer it takes to receive
        packet = client.recv(2**12)
        if not packet: break
        data += packet
    
    msg_size = struct.unpack("Q", data[:HEADERSIZE])[0]
    data = data[HEADERSIZE:]
    
    while len(data) < msg_size:
        data += client.recv(2**12)
        
    pickle_data = data[:msg_size]
    data  = data[msg_size:] # the remainder of data received is stored for the next loop 
    
    frame = pickle.loads(pickle_data)
    cv2.imshow('client', frame)
    cv2.waitKey(10) 

    
client.close()