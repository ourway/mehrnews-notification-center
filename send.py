#!/usr/bin/env python
import sys
import urllib2
import base64
import ujson
import redis
import requests
import time
r=redis.StrictRedis()


url = 'http://www.mehrnews.com/api?place=224'  ## 224
data = requests.get(url).content
if not data:
	print 'no data from mehrnews API server'
	sys.exit()

news = ujson.loads(data)
if not news.get('newsList'):
	print 'Not ant new item available.'
	sys.exit()

newsList = news.get('newsList', [])



# Define relevant info
app_id = 'df617c83'
private_key = 'c31f7ed4a2c581ef545b19f48b08741565674986a2a0d07f'
device_tokens = r.lrange('mehrnews-users-tokens', 0, -1)
url = "https://push.ionic.io/api/v1/push"

# Generate authentication
b64 = base64.encodestring('%s:' % private_key).replace('\n', '')
auth = "Basic %s" % b64

# Build the JSON payload
for i in newsList:
	newsId = i.get('id')
	if str(newsId) in r.lrange('mehrnews-sent-news', 0, -1):
		print 'news %s already sent to users' % newsId
		continue
	push_dict = {}
	notification_dict = {}
	push_dict["tokens"] = device_tokens
	notification_dict["alert"] = i.get('headline')
	push_dict["notification"] = notification_dict

	# Make the request
	req = urllib2.Request(url, data=ujson.dumps(push_dict))
	req.add_header("Content-Type", "application/json")
	req.add_header("X-Ionic-Application-Id", app_id)
	req.add_header("Authorization", auth)
	resp = urllib2.urlopen(req)
	print 'news Item %s sent.' % newsId
	r.lpush('mehrnews-sent-news', newsId)
	time.sleep(10)
