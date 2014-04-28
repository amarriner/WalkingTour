#!/usr/bin/env python
"""
Command line uploader for Vine.
 
For Python 2.7. Batteries included.
Educational/research use only. No warranty. Public domain.
 
usage: vinup.py <username> <video filename> <thumbnail filename> <description>
 
   username           - Your Vine login (email address)
 
   video filename     - Filename for a local MP4 video to upload.
                        Usually this is 480x480 resolution. The server will transcode it
                        to a lower-quality version that the app requests, but this original
                        is available to download too.
 
   thumbnail filename - Filename for a local JPEG thumbnail.
                        Usually this is 480x480 resolution.
 
   description        - A text description for the video. (Remember to quote this properly
                        if it has spaces or other commandline-unfriendly characters.)
 
"""

# From: http://pastebin.com/B5UeWBdb
 
import sys, httplib, urllib, json, hmac, hashlib, base64, uuid, random, getpass
from email.utils import formatdate
 
class APIError(Exception):
    pass
 
def checkStatus(resp):
    if resp.status != 200:
        raise APIError("Status code %d, response %r" % (resp.status, resp.read()))
 
class AmazonS3(object):
    def __init__(self, bucket, accessKey, secret):
        self.host = '%s.s3.amazonaws.com' % bucket
        self.bucketPrefix = '/' + bucket
        self.accessKey = accessKey
        self.secret = secret
        self.conn = httplib.HTTPSConnection(self.host)
        self.headers = {
            'Host': self.host,
            'User-Agent': 'aws-sdk-iOS/1.4.4 iPhone-OS/6.1 en_US',
        }
 
    def _sign(self, msg):
        h = hmac.new(self.secret, msg, hashlib.sha1)
        return base64.encodestring(h.digest()).strip()
 
    def _authorize(self, method, resource, headers):
        headers['Date'] = formatdate(usegmt=True)
        msg = '\n'.join((method, '', headers['Content-Type'], headers['Date'], self.bucketPrefix + resource))
        headers['Authorization'] = "AWS %s:%s" % (self.accessKey, self._sign(msg))
 
    def url(self, resource, versionId):
        return 'https://%s%s?versionId=%s' % (self.host, resource, versionId)
 
    def put(self, resource, contentType, content):
        headers = dict(self.headers)
        headers['Content-Type'] = contentType
        headers['Content-Length'] = len(content)
        self._authorize('PUT', resource, headers)
        self.conn.request('PUT', resource, content, headers)
        resp = self.conn.getresponse()
        checkStatus(resp)
        resp.read()
        return self.url(resource, resp.getheader('x-amz-version-id'))
 
class VineClient(object):
    host = 'api.vineapp.com'
    version = '1.0.5'
 
    def __init__(self):
        self.s3 = AmazonS3('vines', 'AKIAJL2SSORTZ5AK6D4A', 'IN0mNk2we4QqnFaDUUeC7DYzBD9BRCwRYnTutoxj')
        self.conn = httplib.HTTPSConnection(self.host)
        self.headers = {
            'Host': self.host,
            'User-Agent': 'com.vine.iphone/1.0.5 (unknown, iPhone OS 6.1, iPad, Scale/2.000000)',
        }
 
    def _contentId(self):
        return "%s-%d-%016X_%s" % (uuid.uuid4(), random.randint(1024, 0xffff),
            random.randint(0x1000000000, 0xf0000000000), self.version)
 
    def _postForm(self, url, **args):
        headers = dict(self.headers)
        headers['content-type'] = 'application/x-www-form-urlencoded'
        self.conn.request('POST', url, urllib.urlencode(args), headers)
        resp = self.conn.getresponse()
        checkStatus(resp)
        return json.loads(resp.read())
 
    def login(self, username, password):
        r = self._postForm('/users/authenticate', username=username, password=password)
        if not r['success']:
            raise APIError(repr(r['error']))
        self.username = r['data']['username']
        self.userId = r['data']['userId']
        self.headers['vine-session-id'] = r['data']['key']
 
    def upload(self, videoData, thumbData, description):
        cid = self._contentId()
        self._postForm('/posts',
            videoUrl = self.s3.put('/videos/%s.mp4' % cid, 'video/mp4', videoData),
            thumbnailUrl = self.s3.put('/thumbs/%s.mp4.jpg' % cid, 'image/jpeg', thumbData),
            description = description
        )
        return cid
 
def main():
    if len(sys.argv) != 5:
        sys.stderr.write(__doc__)
        sys.exit(1)
 
    _, username, videoFile, thumbFile, desc = sys.argv
    password = getpass.getpass("Password [Vine user %s]: " % username)
 
    videoData = open(videoFile, 'rb').read()
    thumbData = open(thumbFile, 'rb').read()
 
    client = VineClient()
    client.login(username, password)
    print "Successfully logged in. Uploading video..."
    cid = client.upload(videoData, thumbData, desc)
    print "Done. (%s)" % cid
 
if __name__ == '__main__':
    main()
