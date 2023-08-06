import requests
import urllib
from requests.auth import HTTPBasicAuth

class dmail(object):
	
	def __init__(self, msg, auther):
		
		self.user = auther.user
		self.key = auther.key
		
		self.message_id = msg["id"]
		self.owner_id = msg["owner_id"]
		self.from_id = msg["from_id"]
		self.to_id = msg["to_id"]
		self.title = msg["title"]
		self.body = msg["body"]
		
		if msg["is_read"] == "true":
			self.is_read = True
		else:
			self.is_read = False
			
		if msg["is_deleted"] == "true":
			self.is_deleted = True
		else:
			self.is_deleted = False
			
		self.created_at = msg["created_at"]
		
	def delete_msg(self):
		requests.delete("http://danbooru.donmai.us/dmails/$" + self.message_id + ".json", auth=HTTPBasicAuth(self.user, self.key))