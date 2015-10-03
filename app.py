
import falcon
import ujson
import redis

r = redis.StrictRedis()

'''What this module do is very simple.  Just register and unregister tokens.'''
 
class GetToken:
    def on_post(self, req, resp):
        """Handles POST requests"""
	data =  ujson.loads(req.stream.read(4096))
	userData = {}
	if not data.get('unregister', True) and len(data.get('_push', {}).get('android_tokens')):
		userData['token'] = data.get('_push').get('android_tokens')[-1]
		if userData['token'] not in r.lrange('mehrnews-users-tokens', 0, -1):
			r.lpush('mehrnews-users-tokens', userData['token'])
			print 'User %s added to database.' % userData['token']
	else:
		r.lrem('mehrnews-users-tokens', 1, data.get('_push').get('android_tokens')[-1])
		print 'User %s removed from.' % userData['token']
	resp.body=ujson.dumps(data)


	
 
api = falcon.API()
api.add_route('/getToken', GetToken())
