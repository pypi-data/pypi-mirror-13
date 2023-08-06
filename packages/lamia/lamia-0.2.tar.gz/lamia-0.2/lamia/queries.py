import requests
import urllib
from requests.auth import HTTPBasicAuth

class post(object):
	
	def __init__(self, response=None, imgid=None, auther=None):
		if response is None:
			response = requests.get(("https://danbooru.donmai.us/posts/" + str(imgid) + ".json"))
			
		try:
			table = response.json()
		except:
			table = response
			
		self.image_id = table["id"]
		self.creation_date = table["created_at"]
		self.uploader_id = table["uploader_id"]
		self.score = table["score"]
		self.source = table["source"]
		self.md5 = table["md5"]
		self.rating = table["rating"]
		self.width = table["image_width"]
		self.height = table["image_height"]
		self.tag_string = table["tag_string"]
		self.tags = self.tag_string.split(" ")
		self.file_ext = table["file_ext"]
		self.pixiv_id = table["pixiv_id"]
		self.uploader_name = table["uploader_name"]
		self.string_artists = table["tag_string_artist"]
		self.artists = self.string_artists.split(" ")
		self.string_characters = table["tag_string_character"]
		self.characters = self.string_characters.split(" ")
		self.string_copyrights = table["tag_string_copyright"]
		self.copyrights = self.string_copyrights.split(" ")
		self.string_general = table["tag_string_general"]
		self.general_tags = self.string_general.split(" ")
		self.file_url = "http://danbooru.donmai.us" + table["file_url"]
		self.large_file_url = "http://danbooru.donmai.us" + table["large_file_url"]
		if auther is None:
			pass
		else:
			self.user = auther.user
			self.key = auther.key
		
	def download_image(self, path=None):
		if path is None:
			urllib.urlretrieve (self.file_url, (str(self.md5) + "." + str(self.file_ext)))
		else:
			urllib.urlretrieve (self.file_url, (path + (self.md5 + "." + self.file_ext)))
			
	def download_large_image(self, path=None):
		if path is None:
			urllib.urlretrieve (self.file_url, (self.md5 + "." + self.file_ext))
		else:
			urllib.urlretrieve (self.file_url, (path + (self.md5 + "." + self.file_ext)))
			
	def comment_on_post(self, comment):
		url = "http://danbooru.donmai.us/comments.json?comment[post_id]=" + self.image_id + "&comment[body]= " + comment
		requests.post(url, auth=HTTPBasicAuth(self.user, self.key))
	
	def rate_post_up(self):
		requests.post(("http://danbooru.donmai.us/posts/" + self.image_id + "/votes.json?score=up"))
					   
	def rate_post_down(self):
		requests.post(("http://danbooru.donmai.us/posts/" + self.image_id + "/votes.json?score=down"))
					   
	def flag_post(self, reason):
		requests.post(("http://danbooru.donmai.us/post_flags.json/post_flag[post_id]=" + self.image_id + "&post_flag[reason]=" + reason), auth=HTTPBasicAuth(self.user, self.key))
	
	def favorite_post(self):
		requests.post(("http://danbooru.donmai.us/favorites.json?post_id=" + self.post), auth=HTTPBasicAuth(self.user, self.key))
					  
	def unfavorite_post(self):
		requests.delete(("http://danbooru.donmai.us/favorites.json?post_id=" + self.post), auth=HTTPBasicAuth(self.user, self.key))