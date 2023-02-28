#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 01:04:38 2023

@author: shree
"""
from flask import Flask, redirect, render_template, request, Response
import cv2

def feed_generator():
    video = cv2.VideoCapture(0)
    yield b'--frame\r\n'
    while True:
        frame = cv2.imencode('.bmp', video.read()[1])[1].tobytes()
        yield b'Content-Type: image/bmp\r\n\r\n' + frame + b'\r\n--frame\r\n'


host_ip, host_port = "a", "a"
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(feed_generator(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/server")
def server():
    return render_template("server.html")

@app.route("/client", methods=["POST", "GET"])
def client():
    global host_ip, host_port
    if request.method == "POST":
        host_ip = request.form["ip"]
        host_port = request.form["port"]
        print(host_ip, host_port)
    return render_template("client.html")

@app.route("/<usr>")
def user(usr):
    return f"<h1>{usr}</h1>"

if __name__ == "__main__":
    app.run(debug=True, port=5007)