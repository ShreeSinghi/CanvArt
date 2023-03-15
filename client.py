#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 14:14:07 2023

@author: shree
"""

from socket import socket, AF_INET, SOCK_STREAM, gaierror
import cv2
import pickle
import struct
import sys
import converter
import hasher
from time import sleep

# waits until data is entered
def wait_change(glob_vars):
    while not glob_vars["pressed"]:
        sleep(1)
    glob_vars["pressed"] = False
    
def retrieve():
    global data, HEADER_SIZE
    # first we receive the header (size of the pickle file)
    while len(data) < HEADER_SIZE:
        # the smaller the size of datapacket, the longer it takes to receive
        packet = client.recv(2**10)
        if not packet:
            break
        data += packet
    
    msg_size = struct.unpack("Q", data[:HEADER_SIZE])[0]
    data = data[HEADER_SIZE:]
    
    while len(data) < msg_size:
        data += client.recv(2**10)
        
    pickle_data = data[:msg_size]
    data  = data[msg_size:] # the remainder of data received is stored for the next loop 
    
    return pickle.loads(pickle_data)

def feed_generator(glob_vars):
    global data, HEADER_SIZE, client
    
    yield b'--frame\r\n'
    tile_size = 20
    
    hashbin, im_list, bgr_avg = hasher.load_data()
    
    while True:
        try:
############# SERVER STUFF ##################
            host_ip, port = glob_vars["host_ip"], glob_vars["port"]
            print(glob_vars, file=sys.stderr)
        
            client = socket(AF_INET, SOCK_STREAM)
            print("connecting", file=sys.stderr)
            client.connect((host_ip, port))
            print("connected", file=sys.stderr)
            
            data = b""
            
            HEADER_SIZE = struct.calcsize("Q")
            
            glob_vars["message"] = "Connected!"
            
############# VIDEO STUFF #####################
            
            image = retrieve()
            converter.init(image.shape[0], image.shape[1], im_list, bgr_avg, hashbin, w_size=1)
        
            while True:
                image = retrieve()
                converter.convert(image)
            
                frame = cv2.imencode('.png', converter.result_image)[1].tobytes()
                
                yield b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n--frame\r\n'
        except gaierror:
            glob_vars["message"] = "Incorrect input"
            wait_change(glob_vars)
        except ConnectionRefusedError:
            glob_vars["message"] = "Host busy"
            wait_change(glob_vars)
        except (struct.error, ConnectionResetError):
            glob_vars["message"] = "Host disconnected :("
            wait_change(glob_vars)