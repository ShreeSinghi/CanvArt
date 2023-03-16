# Welcome to CanvArt

The core aim of the project is to automatically create a tiling mosaic effect where a larger image is made using a dataset of hundreds of smaller images. The application allows the user to apply this effect using a dataset of their choice and convert images and videos (internally processed frame-by-frame). The user can also behave as a server/client and connect to another PC with the application installed 

The project uses KD Trees and hash tables to find the nearest visually similar image to each tile and ensure real-time video streaming with minimal latency

# Installation guide

 - Clone the repository by using ```git clone github.com/sdswoc/canvart``` 

 - Install Python 3.9.x and run ```pip3 install requirements.txt```
# Usage
```cd``` into the cloned directory and run ```python3 web.py``` on your console. You'll be presented with the flask webpage URL. Copy this link and enter it into your browser to launch the application.
You can choose your dataset of tiler images by uploading jpg files using the button on the top-left corner
 
 ![enter image description here](https://i.imgur.com/d8oXGHS.jpeg)
 
 - You can then choose to either convert videos and images of your choice
 - Or you can choose to be the host of the video stream
	 - Once you load the webpage you can pass the details of the IP address and the port the client has to connect to
- Or you can choose to be the client
	- Enter the IP address and port you need to connect to

Enjoy your super cool video streaming!

![kohli](https://i.imgur.com/WlXyu3J.jpeg)
