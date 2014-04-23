#!/usr/bin/python

from PIL import Image
import json
import math
import subprocess
import urllib

# Read cached JSON from google directions API
# https://maps.googleapis.com/maps/api/directions/json?origin=New%20York%20City,%20USA&destination=Los%20Angeles,%20CA%20USA&mode=walking&sensor=false
f = open('directions.json')
directions = json.loads(f.read())
f.close

# Loop through the steps 
for i in range(102,103):

   # Get the current step for readability 
   step = directions['routes'][0]['legs'][0]['steps'][i]

   # Debug output for given step
   print '-------------------------------------------------------------------------------------------------------'
   print str(i + 1) + '. ' + step['html_instructions']

   # Get a google street view image looking north, east, south, and west
   for x in range(0, 4):
      heading = x * 90
      step_url = 'http://maps.googleapis.com/maps/api/streetview?size=480x480&sensor=false&location=' + \
                    str(step['end_location']['lat']) + ',' + str(step['end_location']['lng']) + \
                    '&heading=' + str(heading)

      print step_url
      urllib.urlretrieve(step_url, 'step' + str(heading) + '.jpg')

   # Get a static map of the end location at a high zoom
   map_url = 'http://maps.googleapis.com/maps/api/staticmap?size=480x240&sensor=false&zoom=6&center=' + \
                str(step['end_location']['lat']) + ',' + str(step['end_location']['lng']) + \
                '&markers=' + str(step['end_location']['lat']) + ',' + str(step['end_location']['lng'])
   print map_url
   urllib.urlretrieve(map_url, 'map.jpg')

   # Get a static map of the path of the step at a closer zoom
   walk_url = 'http://maps.googleapis.com/maps/api/staticmap?'                                + \
              'sensor=false&'                                                                 + \
              'size=480x240&'                                                                 + \
              'markers=color:0x2222dd|label:1|' + str(step['start_location']['lat'])          + \
              ',' + str(step['start_location']['lng']) + '&'                                  + \
              'markers=color:0x2222dd|label:2|' + str(step['end_location']['lat'])            + \
              ',' + str(step['end_location']['lng']) + '&'                                    + \
              'path=geodesic:true|color:0x0000ff60|weight:4|'                                 + \
              str(step['start_location']['lat']) + ',' + str(step['start_location']['lng'])   + \
              '|' + str(step['end_location']['lat']) + ',' + str(step['end_location']['lng'])
   print walk_url
   urllib.urlretrieve(walk_url, 'walk.jpg')

print '-------------------------------------------------------------------------------------------------------'

# For each streetview angle, combine it with the static maps
map_image = Image.open('map.jpg')
walk_image = Image.open('walk.jpg')
for x in range(0, 4):
   angle = x* 90
   step_image = Image.open('step' + str(angle) + '.jpg')

   combo = Image.new(step_image.mode, (960, 480))
   combo.paste(step_image, (0, 0))
   combo.paste(map_image, (480, 0))
   combo.paste(walk_image, (480, 240))

   combo.save('combo' + str(angle) + '.jpg', 'jpeg')

# Build an animated GIF of the static images and each streeview angle
subprocess.call('./make_animated_gif.shl')
