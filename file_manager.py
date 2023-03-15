#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 11:14:54 2023

@author: shree
"""

import cv2
import hasher
import converter
import moviepy.editor as mpy
import os
import shutil

window_size = 10
tile_size = 20

def refresh(directory):
    try:
        shutil.rmtree(directory)
    except Exception:
        pass
    os.makedirs(directory)

    
def init():
    global im_list, bgr_avg, hashbin
    hashbin, im_list, bgr_avg = hasher.load_data()
        
def create_video(path):
    global im_list, bgr_avg, hashbin, window_size, tile_size

    vidcap = cv2.VideoCapture(path)   
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    audio = mpy.VideoFileClip(path).audio

    success = True
    i = 0
    success, image = vidcap.read()
    converter.init(image.shape[0]//window_size, image.shape[1]//window_size,
                   im_list, bgr_avg, hashbin, window_size)
    
    refresh('temp/')
    
    while success:
        converter.convert(image)
        cv2.imwrite(f'temp/{i}.png', converter.result_image)
        i += 1
        success, image = vidcap.read()

    clip = mpy.ImageSequenceClip([f'temp/{x}.png' for x in range(i)], fps=fps)

    clip.audio = audio
    clip.write_videofile(f"converted/{path.split('/')[-1]}", fps=fps)
    
def create_photo(path):
    
    photo = cv2.imread(path)
    
    converter.init(photo.shape[0]//window_size, photo.shape[1]//window_size,
                   im_list, bgr_avg, hashbin, window_size)
    converter.convert(photo)
        
    cv2.imwrite(f"converted/{path.split('/')[-1]}", converter.result_image.copy())
    