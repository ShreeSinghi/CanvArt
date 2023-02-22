#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 14:14:07 2023

@author: shree
"""

from socket import socket, AF_INET, SOCK_STREAM
import cv2
import pickle
import struct
import converter
import hasher

def retrieve():
    global data, HEADER_SIZE
    # first we receive the header (size of the pickle file)
    while len(data) < HEADER_SIZE:
        # the smaller the size of datapacket, the longer it takes to receive
        packet = client.recv(2**12)
        if not packet: break
        data += packet
    
    msg_size = struct.unpack("Q", data[:HEADER_SIZE])[0]
    data = data[HEADER_SIZE:]
    
    while len(data) < msg_size:
        data += client.recv(2**12)
        
    pickle_data = data[:msg_size]
    data  = data[msg_size:] # the remainder of data received is stored for the next loop 
    
    return pickle.loads(pickle_data)

############# SERVER STUFF ##################

client = socket(AF_INET, SOCK_STREAM)
host_ip = '192.168.29.126'
PORT = 11021
client.connect((host_ip, PORT)) 

data = b""  # creates an empty data packet

HEADER_SIZE = struct.calcsize("Q")

############# VIDEO STUFF #####################

im_list = retrieve()
bgr_avg, hashbin = hasher.main(im_list)

image = retrieve()
converter.init(image.shape[0], image.shape[1], im_list, bgr_avg, hashbin, w_size=1)

while True:
    image = retrieve()
    converter.convert(image)

    cv2.imshow('client', converter.result_image)
    cv2.waitKey(10)

client.close()