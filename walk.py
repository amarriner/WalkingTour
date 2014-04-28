#!/usr/bin/python

from PIL import Image, ImageDraw
import json
import keys
import math
import os.path
import re
import subprocess
import twitter
import urllib

pwd = '/home/amarriner/python/walk/'

# Read cached JSON from google directions API
# https://maps.googleapis.com/maps/api/directions/json?origin=New%20York%20City,%20USA&destination=Los%20Angeles,%20CA%20USA&mode=walking&sensor=false
f = open(pwd + 'directions.json')
directions = json.loads(f.read())
f.close

# Get current step
step_index = 0
step_index_file = pwd + 'step.index'
if os.path.isfile(step_index_file):
   f = open(step_index_file)
   step_index = f.read()
   f.close()

# Loop through the steps 
for i in range(int(step_index),int(step_index) + 1):

   # Get the current step for readability 
   step = directions['routes'][0]['legs'][0]['steps'][i]

   # Debug output for given step
   print '-------------------------------------------------------------------------------------------------------'
   instructions = re.sub(r'<[^>]*>', r"", step['html_instructions'])

   if len(step['html_instructions']) > 140:
      end = step['html_instructions'].find('<div')
      instructions = re.sub(r'<[^>]*>', r"", step['html_instructions'][:end])

   step['duration']['text'] = step['duration']['text'].replace(' hours', 'h').replace(' mins', 'm')
   tweet = str(i + 1) + '. ' + instructions + ' (' + step['distance']['text'] + ', ' + \
                                                     step['duration']['text'] + ')'
   print tweet

   # Get a google street view image looking north, east, south, and west
   for x in range(0, 4):
      heading = x * 90
      step_url = 'http://maps.googleapis.com/maps/api/streetview?size=240x240&sensor=false&location=' + \
                    str(step['end_location']['lat']) + ',' + str(step['end_location']['lng']) + \
                    '&heading=' + str(heading) + '&key=' + keys.google_api_key

      print step_url
      urllib.urlretrieve(step_url, pwd + 'step' + str(heading) + '.jpg')

   # Get a static map of the end location at a high zoom
   map_url = 'http://maps.googleapis.com/maps/api/staticmap?size=480x240&sensor=false&zoom=6&center=' + \
                str(step['end_location']['lat']) + ',' + str(step['end_location']['lng']) + \
                '&markers=' + str(step['end_location']['lat']) + ',' + str(step['end_location']['lng']) + \
                '&key=' + keys.google_api_key
   print map_url
   urllib.urlretrieve(map_url, pwd + 'map.jpg')

   # Get a static map of the path of the step at a closer zoom
   walk_url = 'http://maps.googleapis.com/maps/api/staticmap?'                                + \
              'sensor=false&'                                                                 + \
              'format=jpg&'                                                                   + \
              'size=480x240&'                                                                 + \
              'key=' + keys.google_api_key + '&'                                              + \
              'markers=color:0x2222dd|label:1|' + str(step['start_location']['lat'])          + \
              ',' + str(step['start_location']['lng']) + '&'                                  + \
              'markers=color:0x2222dd|label:2|' + str(step['end_location']['lat'])            + \
              ',' + str(step['end_location']['lng']) + '&'                                    + \
              'path=color:0x0000ff60|weight:4|enc:' + step['polyline']['points']
   print walk_url
   urllib.urlretrieve(walk_url, pwd + 'walk.jpg')

   f = open(step_index_file, 'w')
   f.write(str(int(step_index) + 1))
   f.close()

print '-------------------------------------------------------------------------------------------------------'

# For each streetview angle, combine it with the static maps
map_image = Image.open(pwd + 'map.jpg')
walk_image = Image.open(pwd + 'walk.jpg')
combo = Image.new(walk_image.mode, (963, 483))
draw = ImageDraw.Draw(combo)
draw.rectangle([0, 0, 962, 482], fill='#222222')

for x in range(0, 4):
   angle = x * 90
   step_image = Image.open(pwd + 'step' + str(angle) + '.jpg')

   # Terrible kludge to quick fix twitter failing to accept animated GIFs
   # Needs refactoring!   
   if x == 0:
      combo.paste(step_image, (1, 1))
   if x == 1:
      combo.paste(step_image, (242, 1))
   if x == 2:
      combo.paste(step_image, (1, 242))
   if x == 3:
      combo.paste(step_image, (242, 242))

   combo.paste(map_image, (483, 1))
   combo.paste(walk_image, (483, 242))

combo.save(pwd + 'combo.jpg', 'jpeg')

# Connect to Twitter
api = twitter.Api(keys.consumer_key, keys.consumer_secret, keys.access_token, keys.access_token_secret)

# Post tweet text and image
status = api.PostMedia(tweet, pwd + 'combo.jpg')

