from django.db import models
from django.contrib.admin.models import User
from django.contrib import admin
from polardroid import settings

import Image, ImageOps, hashlib

# Create your models here.
class Photo(models.Model):
	title = models.CharField(max_length=50)
	image = models.ImageField(upload_to="original")
	md5 = models.CharField(max_length=50, blank=True, null=True)
	user = models.ForeignKey(User)
	filtered = models.BooleanField(default=False)
	
	def __unicode__(self):
		return self.title
	
	
	def original_path(self):
		return settings.MEDIA_ROOT + '640/' + self.md5 + '.png'
	
	def path(self):
		return settings.MEDIA_ROOT + 'filtered/' + self.md5 + '.jpg'
		
	def url(self):
		if self.filtered:
			return settings.MEDIA_URL + 'filtered/' + self.md5 + '.jpg'
		else:
			return settings.MEDIA_URL + '640/' + self.md5 + '.png'
			
	def resize(self):
		size = 640,640
		try:
			img = Image.open(self.image)
			md5sum = hashlib.md5(img.tostring()).hexdigest()
			self.md5 = md5sum		
			
			img = ImageOps.fit(img, size, Image.ANTIALIAS, 0, (0.5,0.5))
			img.save(self.original_path(), "PNG")
		except IOError:
			print "Cannot create resized image for ", self.image

admin.site.register(Photo)	

# -- DJANGO SOCIAL AUTH REGISTRATION
from social_auth.signals import socialauth_registered

def new_users_handler(sender, user, response, details, **kwargs):
	print sender
	print user
	print response
	print details
	for key, value in kwargs:
		print "%s:%s" % key, value
	
	return False

socialauth_registered.connect(new_users_handler, sender=None)
