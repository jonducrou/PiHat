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
from functools import partial

from PIL import Image
import zbar

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

#effects
smiley_face="smiley face"
vertical_hold="vhold"
trippy_colours="trippy"
effect_off="effect off"  #admin effect

#screen sizes
pic_in_pic="pic in pic"
full_video="video"
full_camera="camera"
off="off"    #admin control

#initial values
effect=effect_off
screen_size=pic_in_pic
admin=False

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.

    """
    def on_data(self, data):
        global a_time_to_die, stream, admin, effect, screen_size
        if a_time_to_die:
          return False
        user_name = json.loads(data)['user']['screen_name'].encode('utf-8')
        tweet_text = json.loads(data)['text'].encode('utf-8')
        if user_name == "kangahooroo":
            admin = True
        effect = self.calculate_effect(tweet_text)
        screen_size = self.calculate_screen(tweet_text)
        admin = False  #set back to false after calculating effect so admin doesn't stay on
        text = "[b]"
        text += user_name
        text += "[/b]: "
        text += tweet_text
        text = '\n'.join(tw.wrap(text))
        tweets.append((text,int(round(time.time() * 1000))))
        update_text()
        print "Twit!"
        return True

    def on_error(self, status):
        print status

    def calculate_effect(self, tweet_text):
        if smiley_face in tweet_text:
            return smiley_face
        if vertical_hold in tweet_text:
            return vertical_hold
        if trippy_colours in tweet_text:
            return trippy_colours
        if effect_off in tweet_text and admin:
            return effect_off
        return effect

    def calculate_screen(self, tweet_text):
        if pic_in_pic in tweet_text:
            return pic_in_pic
        if full_video in tweet_text:
            return full_video
        if full_camera in tweet_text:
            return full_camerac
        if off in tweet_text and admin:
            return off
        return screen_size

if __name__ == '__main__': 
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['piano'], async=True)
    print "Twitter enabled"



tweets = []

def update_text(dt=0):
  global tweets
  millis = int(round(time.time() * 1000))
  x = []
  for t in tweets:
    if millis - t[1] < 60000:
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

def on_position_change(instance, value=0):
  global pv
  global feed_data, feed_width, feed_height, feed_ready
  if int(value) > pv:
    pv = value

def camera_loop(instance, dt=0):
  global feed_ready
  if feed_ready:  
    texture = Texture.create(size=(feed_width, feed_height))
    texture.blit_buffer(feed_data, colorfmt='rgb', bufferfmt='ubyte')
    instance.canvas.after.clear()
# FULL SCREEN
    instance.canvas.after.add(Rectangle(texture=texture, pos=(0,0), size=(instance.width, instance.height)))
# PIC IN PIC
#    instance.canvas.after.add(Rectangle(texture=texture, pos=(instance.width - feed_width, instance.height-feed_height), size=(feed_width, feed_height)))
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

face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')

faces = None

def detect_faces(img):
    global faces
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        cv2.circle(img, (x+w/2, y+h/2), w/2, (0,255,255), -1 )
        cv2.circle(img, (x+w/3, y+h/5), w/10, (0,0,0), -1 )
        cv2.circle(img, (x+2*w/3, y+h/5), w/10, (0,0,0), -1 )
        cv2.circle(img, (x+w/2, y+3*h/4), w/5, (0,0,0), -1 )
        cv2.circle(img, (x+w/2, y+h/2), w/2, (0,0,0), 3 )
    return img       
 
class VideoPlayerApp(App):

    def build(self):
        global feed_thread
        if len(argv) > 1:
            filename = argv[1]
        else:
            curdir = dirname(__file__)
            filename = join(curdir, 'softboy.avi')
        Window.clearcolor = (0, 0, 0, 1)
        layout = FloatLayout(size=(300, 300))
        self.v = FullVideo(source=filename, state='play', volume = 0, options={'allow_stretch': True})#, pos_hint={'y':.2})
        Clock.schedule_interval(partial(camera_loop, self.v), 0.05)
        Clock.schedule_interval(update_text,1)
        self.v.bind(position=on_position_change)
        layout.add_widget(self.v)
        Window.bind(on_key_down=on_key)
        layout.add_widget(tweet)
        feed_thread = Thread(target = self.get_feed)
        feed_thread.start()

        return layout


        
    
    def get_feed(self):
      global a_time_to_die, feed_data, feed_width, feed_height, feed_ready
      scanner = zbar.ImageScanner()
      scanner.parse_config('enable')
      shift = 1

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
          try:
#            print "qr time"
#            pil_im = Image.fromarray(data)
#            image = zbar.Image(width, height, 'Y800', pil_im.tostring())
#            scanner.scan(image)
#            for symbol in image:
#              print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
#            del(image)
#          except:
#            print "qr fail"

#            data = cv2.flip(detect_faces(cv2.flip(data, 0)),0)
 #         except:
  #          print "face fail"

#            shift += 1
 #           data += shift % 256
  #        except:
   #         print "shift fail"

            shift += 10
            M = numpy.float32([[1,0,0],[0,1,shift%height]])
            data1 = cv2.warpAffine(data,M,(width,height))
            M = numpy.float32([[1,0,0],[0,1,(shift%height)-height]])
            data2 = cv2.warpAffine(data,M,(width,height))
            data = data1 + data2
            M = numpy.float32([[1,0,shift%width],[0,1,0]])
            data1 = cv2.warpAffine(data,M,(width,height))
            M = numpy.float32([[1,0,(shift%width)-width],[0,1,0]])
            data2 = cv2.warpAffine(data,M,(width,height))
            data = data1 + data2
          except:
            print "vhold fail"

          data = cv2.cvtColor(data,cv2.COLOR_BGR2RGB)
          feed_data = data.tostring()
          feed_width = width
          feed_height = height
          feed_ready = True
          sleep(.001)
        except: 
          s.close()
          print("fail")
          sleep(25)

if __name__ == '__main__':
    VideoPlayerApp().run()



