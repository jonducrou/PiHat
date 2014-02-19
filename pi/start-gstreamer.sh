#!/bin/sh

sleep 15
raspivid -hf -t 0 -h 480 -w 640 -fps 25 -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse !  rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=192.168.1.221 port=5000
echo "Up!"
