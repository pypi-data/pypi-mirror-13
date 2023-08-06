import requests
import queries
import dmails
import wiki
from requests.auth import HTTPBasicAuth

class api(object):
	
	def __init__(self, user, key):
		self.user = user
		self.key = key
		
	def create_image(self, image_id):
		image_table = requests.get(("http://danbooru.donmai.us/posts/" + image_id + ".json"), auth=HTTPBasicAuth(self.user, self.key))
		image = queries.post(image_table, image_id, self)
		
		return image
	
	def search_images(self, tag_string, pages):
		results = []	
		for i in xrange(pages):
			search = requests.get(("http://danbooru.donmai.us/posts.json?limit=20&page=" + str(i) + "&tags=" + tag_string), auth=HTTPBasicAuth(self.user, self.key))
			table = search.json()
			for posts in table:
				img = queries.post(posts, None, self)
				results.append(img)
				
		return results
		
	def upload(self, filepath, rating, tag_string, source=""):
		files = {'file': open(filepath)}
		requests.post(("http://danbooru.donmai.us/uploads.json?upload[file]=" + filepath + "&upload[source]=" + source + "?upload[rating]=" + rating + "?upload[tag_string]=" + tag_string),
			auth=HTTPBasicAuth(self.user, self.key), files=files)
	
	def get_dmails(self):
		mails = []
		mailbox = requests.get("http://danbooru.donmai.us/dmails.json", auth=HTTPBasicAuth(self.user, self.key))
		dmailbox = mailbox.json()
		for mail in dmailbox:
			msg = dmails.dmail(mail, self)
			mails.append(msg)
			
		return mails
	
	def send_dmail(self, title, body, to):
		requests.post("http://danbooru.donmai.us/dmails.json?dmail[to_name]=" + to + "&dmail[title]=" + title + "&dmail[body]=" + body, auth=HTTPBasicAuth(self.user, self.key))
		
	def create_entry(self, title, body):
		requests.post(("http://danbooru.donmai.us/wiki_pages.json?wiki_page[title]=" + str(title) + "&wiki_page[body]=" + str(body)),
					 auth=HTTPBasicAuth(self.user, self.key))
		
	def get_entries(self, terms):
		results = []
		search = requests.get(("http://danbooru.donmai.us/wiki_pages.json?search[title]=" + terms), auth=HTTPBasicAuth(self.user, self.key))
		table = search.json()
		for entries in table:
			entry = wiki.entry(entries, self)
			results.append(entry)
		
		return results