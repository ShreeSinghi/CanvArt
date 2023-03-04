#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 01:04:38 2023

@author: shree
"""
from flask import Flask, redirect, render_template, request, Response, session
from flask_session import Session
import server
import json
import sys
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
import psutil

def get_ips():
    ips = dict()
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == AF_INET and interface:
                ips[interface] = snic.address
    return ips

app = Flask(__name__)
app.config.from_object(__name__)
Session(app)

def server_connect():
    global client_socket, server_socket, HOST_IP, PORT, connected
    
    ips = get_ips()
    
    server_socket = socket(AF_INET, SOCK_STREAM)
    
    for key in ips.keys():
        if key.startswith('wlp'):
            HOST_IP = ips[key]
            break
    else:
        HOST_IP = '127.1.1.1'
    server_socket.bind((HOST_IP, 0))

    PORT = server_socket.getsockname()[1]

    with open('data.txt', 'w') as f:
        f.write(f"{HOST_IP} {PORT}")

    server_socket.listen(4)
    
    print('Listening', file=sys.stderr)
    
    client_socket, addr = server_socket.accept()
    print(f'Connected to: {addr}', file=sys.stderr)
    connected = True


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    global client_socket
    return Response(server.feed_generator(client_socket),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status', methods=['GET'])
def getStatus():
  status_list = {'HOST_IP': HOST_IP, 'PORT': str(PORT), 'connected': str(connected)}
  return json.dumps(status_list)


@app.route("/server")
def server_page():
    global HOST_IP, PORT, connected
    HOST_IP, PORT, connected = "", 0, False

    t = Thread(target=server_connect)
    t.start()
    return render_template("server.html")

@app.route("/client", methods=["POST", "GET"])
def client_page():
    return render_template("client.html")


if __name__ == "__main__":
    app.run(debug=True, port=5034)