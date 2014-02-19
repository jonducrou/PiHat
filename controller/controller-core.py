import os
import kivy
kivy.require('1.2.0')
import json
from sys import argv
from os.path import dirname, join
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import *
from kivy.graphics.texture import Texture
from kivy.uix.video import Video
from kivy.config import Config
#Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'show_cursor', 0)
from time import sleep
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty, ListProperty, \
    AliasProperty, BooleanProperty, NumericProperty
import time
import textwrap
import socket
import cv2
import numpy
import pickle
from threading import Thread

feed_thread = None
a_time_to_die = False

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream


consumer_key="wjvjcwu1NlowLwZfkGcPqw"
consumer_secret="OWuns50vFWFC0iQvkXmLvntytN2U2TNrUK8U0taXu0"


access_token="2349037988-7qZorUKpZ4QINjdMDWbGcHhkgsuPoUl70SJeDeU"
access_token_secret="u6U0zXHkaxwI6O1qtLcu94wgn6DY7teCUiZaWjS7RS8Nl"

tw = textwrap.TextWrapper(width=80)

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        global a_time_to_die
        if a_time_to_die:
          self.disconnect()
        text = "[b]"
        text += json.loads(data)['user']['screen_name'].encode('utf-8')
        text += "[/b]: "
        text += json.loads(data)['text'].encode('utf-8')
        text = '\n'.join(tw.wrap(text))
        tweets.append((text,int(round(time.time() * 1000))))
        update_text()
        print "Twit!"
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__': 
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['piano'], async=True)
    print "Twitter enabled"



tweets = []

def update_text():
  global tweets
  millis = int(round(time.time() * 1000))
  x = []
  for t in tweets:
    if millis - t[1] < 15000:
      x.append(t)
  tweets = x
  text = '\n\n'.join([x[0] for x in tweets[:4]])
  tweet.text = text

pv = 0

def recvall(sock):
    data = ""
    part = None
    while part is None or len(part) == 16*1024:
        part = sock.recv(16*1024)
        data+=part
    return data

def on_position_change(instance, value):
  global pv
  global feed_data, feed_width, feed_height, feed_ready
  if int(value) > pv:
    pv = value
    update_text()
  if feed_ready:  
    texture = Texture.create(size=(feed_width, feed_height))
    texture.blit_buffer(feed_data, colorfmt='rgb', bufferfmt='ubyte')
    instance.canvas.after.clear()
    instance.canvas.after.add(Rectangle(texture=texture, pos=(instance.width - feed_width, instance.height-feed_height), size=(feed_width, feed_height)))
    feed_ready = False

def on_key(instance, keyboard, keycode, text, modifiers):
        global a_time_to_die
        print('The key is', text)
        if text == 'q':
           stream.disconnect()
           a_time_to_die = True
           exit(0)

tweet = Label(text='Hello! ',pos=(0,-180), markup=True, font_size=28)



class FullVideo(Video):
    pass
    def get_norm_image_size(self):
        if not self.texture:
            return self.size
        ratio = self.image_ratio
        w, h = self.size
        tw, th = self.texture.size

        # ensure that the width is always maximized to the containter width
        if self.allow_stretch:
            if not self.keep_ratio:
                return w, h
            iw = w
        else:
            iw = min(w, tw)
        # calculate the appropriate height
        ih = iw / ratio
        # if the height is too higher, take the height of the container
        # and calculate appropriate width. no need to test further. :)
        if ih > h:
            if self.allow_stretch:
                ih = h
            else:
                ih = min(h, th)
            iw = ih * ratio

        return iw, ih
    norm_image_size = AliasProperty(get_norm_image_size, None, bind=(
        'texture', 'size', 'image_ratio', 'allow_stretch'))


feed_data = None
feed_width = 1
feed_height = 1
feed_ready = False
        
class VideoPlayerApp(App):

    def build(self):
        global feed_thread
        if len(argv) > 1:
            filename = argv[1]
        else:
            curdir = dirname(__file__)
            filename = join(curdir, 'softboy.avi')
        layout = FloatLayout(size=(300, 300))
        self.v = FullVideo(source=filename, state='play', volume = 0, options={'allow_stretch': True})#, pos_hint={'y':.2})
        
        self.v.bind(position=on_position_change)
        layout.add_widget(self.v)
        Window.bind(on_key_down=on_key)
        layout.add_widget(tweet)
        feed_thread = Thread(target = self.get_feed)
        feed_thread.start()

        return layout


        
    
    def get_feed(self):
      global a_time_to_die, feed_data, feed_width, feed_height, feed_ready
      while 1: 
        if a_time_to_die:
          return
        try:
          HOST = ''    # The remote host
          PORT = 12345              # The same port as used by the server
          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          s.connect((HOST, PORT))
          s.send('Yo!')
          data = data = recvall(s)
          s.close()
          data = pickle.loads(data)
          #print 'Received img' 
          height, width, depth = data.shape
          data = cv2.cvtColor(data,cv2.COLOR_BGR2RGB)
          feed_data = data.tostring()
          feed_width = width
          feed_height = height
          feed_ready = True
          sleep(.05)
        except: 
          s.close()
          print("fail")
          sleep(25)

if __name__ == '__main__':
    VideoPlayerApp().run()



