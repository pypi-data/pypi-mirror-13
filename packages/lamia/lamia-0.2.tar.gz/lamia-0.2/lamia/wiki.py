import requests
import urllib
from requests.auth import HTTPBasicAuth

class entry(object):
	
	def __init__(self, page, auther):
		self.user = auther.user
		self.key = auther.key
		
		self.id_number = page["id"]
		self.created_at = page["created_at"]
		self.last_update = page["updated_at"]
		self.title = page["title"]
		self.body = page["body"]
		self.creator_id = page["creator_id"]
		
		if page["is_locked"] == "false":
			self.is_locked = False
		else:
			self.is_locked = True
			
		self.other_names = page["other_names"]
		self.creator_name = page["creator_name"]
		
	def update_title(self, title):
		requests.put(("http://danbooru.donmai.us/wiki_pages/" + str(self.id_number) + ".json?wiki_page[title]=" + str(title) + "&wiki_page[body]=" + self.body),
					 auth=HTTPBasicAuth(self.user, self.key))
		
	def update_body(self, body):
		requests.put(("http://danbooru.donmai.us/wiki_pages/" + str(self.id_number) + ".json?wiki_page[title]=" + self.title + "&wiki_page[body]=" + str(body)),
					 auth=HTTPBasicAuth(self.user, self.key))