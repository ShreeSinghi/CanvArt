#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 12:57:44 2023

@author: shree
"""
import struct
import cv2
import pickle
import hasher
import converter
from socket import socket, AF_INET, SOCK_STREAM
import psutil
import sys

def get_ips():
    ips = dict()
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == AF_INET and interface:
                ips[interface] = snic.address
    return ips

def send(array, client):
    pickle_data = pickle.dumps(array)
    
    # size of pickle is stored in a long long int (represented by Q)
    message = struct.pack("Q", len(pickle_data)) + pickle_data
    client.sendall(message)


def feed_generator(glob_vars):
    video = cv2.VideoCapture(0)

    window_size = 20
    
    yield b'--frame\r\n'
    
    while True:
        try:
    
    ################# SERVER STUFF #####################
            ips = get_ips()
            
            server_socket = socket(AF_INET, SOCK_STREAM)
            
            for key in ips.keys():
                if key.startswith('wlp'):
                    glob_vars["host_ip"] = ips[key]
                    break
            else:
                glob_vars["host_ip"] = '127.1.1.1'
                
            server_socket.bind((glob_vars["host_ip"], 0))
        
            glob_vars["port"] = server_socket.getsockname()[1]
        
            server_socket.listen(4)
            client, addr = server_socket.accept()
            glob_vars["message"] = ""
            
    ################# VIDEO STUFF #####################
            
            hashbin, im_list, bgr_avg = hasher.load_data()
            
            showing, image = video.read()
            
            converter.init(image.shape[0]//window_size, image.shape[1]//window_size,
                           im_list, bgr_avg, hashbin, window_size)
            
                    
            while True:
                
                image = video.read()[1]
                small_image = converter.convert(image)    
                
                send(small_image, client)
                
                frame = cv2.imencode('.bmp', converter.result_image)[1].tobytes()
                
                yield b'Content-Type: image/bmp\r\n\r\n' + frame + b'\r\n--frame\r\n'
                
        except ConnectionResetError:
            glob_vars["message"] = "CLIENT DISCONNECTED!"
            