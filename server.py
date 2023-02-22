#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 12:57:44 2023

@author: shree
"""
import struct
import cv2
from socket import socket, AF_INET, SOCK_STREAM
import pickle
import hasher
import converter
import psutil

def get_ips():
    ips = dict()
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == AF_INET and interface:
                ips[interface] = snic.address
    return ips

def send(array):
    pickle_data = pickle.dumps(array)
    
    # size of pickle is stored in a long long int (represented by Q)
    message = struct.pack("Q", len(pickle_data)) + pickle_data
    client.sendall(message)

############# SERVER STUFF ##################

ips = get_ips()

server = socket(AF_INET, SOCK_STREAM)

for key in ips.keys():
    if key.startswith('wlp'):
        host_ip = ips[key]
        break
else:
    host_ip = '127.0.1.1'

PORT = 11021
print('HOST IP and PORT:', host_ip, PORT)

socket_address = (host_ip, PORT)
server.bind(socket_address)
server.listen(5)

print('Listening')

client, addr = server.accept()
print(f'Connected to: {addr}')

############# VIDEO STUFF #####################

window_size = 20
tile_size = 20

im_list = hasher.create_imarray(tile_size, 'subimages')
send(im_list)
bgr_avg, hashbin = hasher.main(im_list)

video = cv2.VideoCapture(0)
showing, image = video.read()

converter.init(image.shape[0]//window_size, image.shape[1]//window_size,
               im_list, bgr_avg, hashbin, window_size)


try:    
    # if client:
                    
        while(video.isOpened()):
            
            image = video.read()[1]
            small_image = converter.convert(image)    
            
            send(small_image)

            cv2.imshow('original', small_image)
            cv2.imshow('new', converter.result_image)
            
            cv2.waitKey(10)   
                

                
except KeyboardInterrupt:
    client.close()
    video.release()