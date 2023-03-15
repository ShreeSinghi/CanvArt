#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 01:04:38 2023

@author: shree
"""
# redirect if files not loaded
from flask import Flask, render_template, request, Response, send_file, redirect
import server
import client
import file_manager
import json
import sys
import os
import hasher
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

app = Flask(__name__)
app.secret_key = "WoC"
glob_vars = {"host_ip":"", "port":"", "message":"upload .jpg"}

# is the hashtable generated?
loaded = len(os.listdir('data')) == 3

@app.route("/")
def home():
    glob_vars["message"] = "upload .jpg"
    return render_template("index.html")

@app.route("/upload_convert", methods=["POST"])
def upload_convert():
    file_manager.init()
    
    glob_vars["message"] = ""
    
    uploaded_files = request.files.getlist("file")
    print(uploaded_files, file=sys.stderr)

    file_manager.refresh('uploaded/')
    file_manager.refresh('converted/')
    
    for i, file in enumerate(uploaded_files):
        if file.filename.endswith('.jpg') or file.filename.endswith('.mp4'):
            with open(f'uploaded/{file.filename}', 'wb') as f: 
                f.write(file.read())
                print(file.filename, file=sys.stderr)
    
    uploaded_files = [f"uploaded/{file}" for file in os.listdir('uploaded')]
    for file in uploaded_files:
        glob_vars["message"] = file.split("/")[-1]
        if file.endswith('.mp4'):
            file_manager.create_video(file)
        else:
            file_manager.create_photo(file)
    
    zipf = ZipFile('converted files.zip','w', ZIP_DEFLATED)
    for file in os.listdir('converted/'):
        zipf.write(f'converted/{file}')
    zipf.close()
    
    return send_file('converted files.zip',
                     mimetype='zip',
                     as_attachment=True)

@app.route("/upload", methods=["POST"])
def upload():
    global loaded
    
    loaded = False
    tile_size = 20
    glob_vars["message"] = "uploading!"
    
    uploaded_files = request.files.getlist("file")
    print(uploaded_files, file=sys.stderr)

    shutil.rmtree('subimages/')
    os.makedirs('subimages/')
    
    for i, file in enumerate(uploaded_files):
        if file.filename.endswith('.jpg'):
            with open(f'subimages/{file.filename}', 'wb') as f: 
                f.write(file.read())
                print(file.filename, file=sys.stderr)
            
    im_list = hasher.create_imarray(tile_size, 'subimages')
    bgr_avg, hashbin = hasher.main(im_list)
    hasher.save_data(hashbin, im_list, bgr_avg)
    
    loaded = True
    glob_vars["message"]="upload .jpg"
    return redirect("/")
    
@app.route('/feed_server')
def video_server():
    return Response(server.feed_generator(glob_vars),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/feed_client')
def video_client():
    return Response(client.feed_generator(glob_vars),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status', methods=['GET'])
def server_status():
    return json.dumps(glob_vars)

@app.route("/convert")
def convert():
    if loaded:
        glob_vars["message"] = ""
        return render_template("convert.html")
    else:
        return redirect("/")

@app.route("/server")
def server_page():
    global glob_vars
    glob_vars = {"host_ip":"", "port":"", "message":""}
    
    if loaded:
        return render_template("server.html")
    else:
        return redirect("/")
    
@app.route("/client", methods=["POST", "GET"])
def client_page():
    global glob_vars
    glob_vars = {"host_ip":"", "port":"", "message":" ", "pressed":False}
    if request.method == "POST":
        glob_vars["message"] = "Connecting..."
        glob_vars["host_ip"] = str(request.form['ip'])
        if request.form['port'] == "":
            glob_vars["port"] = 0
        else:
            glob_vars["port"] = int(request.form['port'])
        glob_vars["pressed"] = True
        return render_template("client.html", video_url="/feed_client")
    
    if loaded:
        return render_template("client.html", video_url="")
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=4018)