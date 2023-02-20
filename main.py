#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 23:39:28 2023

@author: shree

"""
import numpy as np
import cv2
import PIL
from matplotlib import pyplot as plt
from hasher import im_list, bgr_avg, hashbin, TILE_SIZE

# can be optimised by creating a global "temporary" variable so that memory doesn't
# have to be created and freed repeatedly
def shift_colour(image, dH, dL, dS):
    image = image.astype(float)
    # image[:, :, 0] = (image[:, :, 0]+dH)%181
    # image[:, :, 1] = np.clip(image[:, :, 1] + dL, 0, 255)
    # image[:, :, 2] = np.clip(image[:, :, 2] + dS, 0, 255)

    return cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_HLS2BGR)

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
    numpy tensor representing the scaled image

    """

    # chops down right and lower side of image if indivisible

    height, width, _ = image.shape

    # takes average of pixel values
    image  = cv2.resize(image, dsize=(width//window_size, height//window_size), interpolation=cv2.INTER_CUBIC)

    return image

video = cv2.VideoCapture(0)

while(video.isOpened()):
    showing, image = video.read()

    # image = np.array(PIL.Image.open('christ.jpg'))
    image = tile_down(image, 8)[:,:,::-1]

    cv2.imshow('original', image)

    # we adjust the average hsv values
    # we create an empty rgb image and fill it up using the hashbin we've created

    new_image = np.zeros((image.shape[0]*TILE_SIZE, image.shape[1]*TILE_SIZE, 3))

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            b, g, r = image[i, j]
            new_image[i*TILE_SIZE: (i+1)*TILE_SIZE, j*TILE_SIZE: (j+1)*TILE_SIZE] = im_list[hashbin[g, b, r]]
            # okay idk why but due to some very weird bug i have to look at index gbr, not bgr

    cv2.imshow('new', new_image[:,:,::-1]/255)


    key = cv2.waitKey(10)