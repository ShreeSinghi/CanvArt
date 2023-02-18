#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 23:39:28 2023

@author: shree

remember to deal with the case where two images have same hue and saturation
"""

import numpy as np
import cv2
import PIL
from matplotlib import pyplot as plt
import os

def center_crop(image, resize_dim):

    height, width, _ = image.shape
    if height>width:
        image = image[round(height/2 - width/2): round(height/2 + width/2), :]
    else:
        image = image[:, round(width/2 - height/2): round(width/2 + height/2)]
    
    image  = cv2.resize(image, dsize=(resize_dim, resize_dim), interpolation=cv2.INTER_CUBIC)
    return image

def tile_down(image, window_size):
    """
    Parameters
    ----------
    image : np.array
        the image to be tiled
        
    window_size : int
        size of tile

    Returns
    -------
    None.

    """
    
    # chops down right and lower side of image if indivisible
    
    height, width, _ = image.shape
    
    right_index = width-(width%window_size)
    lower_index = height-(height%window_size)
    
    image = image[:lower_index, :right_index]
    
    # takes average of pixel values
    image  = cv2.resize(image, dsize=(width//window_size, height//window_size), interpolation=cv2.INTER_CUBIC)
    
    # image = image.reshape(height//window_size, window_size,
    #                       width//window_size, window_size, 3)
    # image = image.mean(axis=1).mean(axis=2)
    
    plt.imshow(image/255)
    
    

image = np.array(PIL.Image.open('christ.jpg'))
tile_down(image, 30)

# load all jpg images in an array of bgr
im_list = filter(lambda x: x.lower().endswith('.jpg') or x.lower().endswith('.jpeg'), os.listdir('subimages'))
im_list = map(lambda x: center_crop(np.array(PIL.Image.open(f'subimages/{x}')), 100), im_list)
im_list = list(im_list)

# get average rgb values of each image and convert the average to hls
hls_avg = np.array(im_list).astype('float64').mean(axis=1).mean(axis=1)
hls_avg = cv2.cvtColor(hls_avg[None, :, :].astype(np.uint8), cv2.COLOR_BGR2HLS).reshape(-1, 3)

# this is a hashbin that contains the index of the image (in im_list)
# that should be referred for each point in hue-saturation space, hence number of input images
# must be limited (keep in mind later)
hashbin = np.zeros((180, 256), dtype=np.int16)-1

# contains tuples of the form (saturation, index in im_list) for each image of that hue
hue_list = [list() for i in range(180)]


for i, hls in enumerate(hls_avg):
    hue_list[hls[0]].append((int(hls[2]), i))

# for each hue we "fill" all unknown saturation values with closest image
for hue in range(180):
    if not hue_list[hue]:
        continue
    
    if len(hue_list[hue]) == 1:
        hashbin[hue, :] = hue_list[hue][0][1]
        continue
    
    hue_list[hue].sort()
    hashbin[hue, :(hue_list[hue][0][0] + hue_list[hue][1][0])//2]   = hue_list[hue][0][1]
    hashbin[hue, (hue_list[hue][-1][0] + hue_list[hue][-2][0])//2:] = hue_list[hue][-1][1]
    
    for (sat_next, _), (sat_curr, index), (sat_prev, _) in zip(hue_list[hue][2:], hue_list[hue][1:-1], hue_list[hue][0:-2]):
        hashbin[hue, (sat_prev+sat_curr)//2:(sat_next+sat_curr)//2] = index
    