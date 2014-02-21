#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys

if len(sys.argv) < 3:
  print "I need the IP to pull from and the port to share on"
  exit (1)

import cv2
import os
import gi
import numpy
import Image
gi.require_version("Gtk", "3.0")
gi.require_version("Gst", "1.0")

"""
    GdkX11   @ get_xid()
    GstVideo @ xvimagesink
"""

from gi.repository import GObject, Gst, Gtk, Gdk, GdkX11, GstVideo, GdkPixbuf, GLib

import asyncore
import pickle
import socket
from threading import Thread

a_time_to_die = False

class Player(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.image = None
        GLib.timeout_add(50, self.save_image)
        self.connect("delete-event", self.on_quit)
        # Status
        self.status = Gst.State.NULL
        # Video Area
        self.video_area = Gtk.DrawingArea()
        # Disable Double Buffered
        self.video_area.set_double_buffered(False)
        # playbin
        self.player = Gst.parse_launch("tcpclientsrc host=" + sys.argv[1] +" port=5000 ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert ! xvimagesink name=xv")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)
        # DnD
        dnd_list = Gtk.TargetEntry.new("text/uri-list", 0, 0)
        # pack
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0) 
        vbox.pack_start(self.video_area, True, True, 0)
        self.add(vbox)
        self.resize(640, 480)
        self.show_all()
        self.player.set_state(Gst.State.PLAYING)
        
    def on_quit(self, widget, data=None):
        global a_time_to_die
        a_time_to_die = True
        self.player.set_state(Gst.State.NULL)
        Gtk.main_quit()

    def on_sync_message(self, bus, message):
        if message.get_structure().get_name() == "prepare-window-handle":
            xid = self.video_area.props.window.get_xid()
            imagesink = message.src
            #imagesink.props.force_aspect_ratio = False
            imagesink.set_window_handle(xid)

    def on_message(self, bus, message):
        
        t = message.type
        print t
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.on_quit(None)
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            self.on_quit(None)

    def save_image(self):
      GLib.timeout_add(100, self.save_image)
      #print("save")
      window = self.video_area.get_window()
      pb = Gdk.pixbuf_get_from_window(window, 0, 0, window.get_width(),window.get_height())

      dimensions = pb.get_width(), pb.get_height()
      stride = pb.get_rowstride()
      pixels = pb.get_pixels()
      mode = pb.get_has_alpha() and "RGBA" or "RGB"
      pil_image = Image.frombuffer(mode, dimensions, pixels,
                            "raw", mode, stride, 1)
      open_cv_image = numpy.array(pil_image) 
      open_cv_image = open_cv_image[:, :, ::-1].copy() 
      #cv2.imwrite('/tmp/cimg.png',open_cv_image)
      self.image = open_cv_image


    def get_image(self):
      return self.image

def start_server():
  global a_time_to_die
  HOST = ''                 # Symbolic name meaning the local host
  PORT = int(argv[2])              # Arbitrary non-privileged port  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  socket.timeout(10)
  try:
    s.bind((HOST, PORT))
  except:
    print "Epic fail"
    os._exit(1)
  s.listen(1)
  while 1:
   if a_time_to_die:
     return
   try:
    conn, addr = s.accept()
    #print 'Connected by', addr
    data = conn.recv(1024)
    conn.send(pickle.dumps(player.get_image()))
   finally:
    conn.close()




if __name__ == "__main__":
    GObject.threads_init()
    Gst.init(None)
    player = Player()
    thread = Thread(target = start_server, args = ())
    thread.start()
    Gtk.main()
