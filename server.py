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
import psutil

def send(array, client):
    pickle_data = pickle.dumps(array)
    
    # size of pickle is stored in a long long int (represented by Q)
    message = struct.pack("Q", len(pickle_data)) + pickle_data
    client.sendall(message)


def feed_generator(client):
    
    ################# VIDEO STUFF #####################
    
    window_size = 20
    tile_size = 20
    
    im_list = hasher.create_imarray(tile_size, 'subimages')
    send(im_list, client)
    bgr_avg, hashbin = hasher.main(im_list)
    
    video = cv2.VideoCapture(0)
    showing, image = video.read()
    
    converter.init(image.shape[0]//window_size, image.shape[1]//window_size,
                   im_list, bgr_avg, hashbin, window_size)
    
    yield b'--frame\r\n'
        
    try:    
        if client:
            while True:
                
                image = video.read()[1]
                small_image = converter.convert(image)    
                
                send(small_image, client)
                
                frame = cv2.imencode('.bmp', converter.result_image)[1].tobytes()
                
                yield b'Content-Type: image/bmp\r\n\r\n' + frame + b'\r\n--frame\r\n'
                                    
    except KeyboardInterrupt:
        client.close()
        video.release()