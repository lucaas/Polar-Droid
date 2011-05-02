from django.db import models

from polardroid import settings

import Image, ImageOps, hashlib

# Create your models here.
class Photo(models.Model):
	title = models.CharField(max_length=50)
	image = models.ImageField(upload_to="original")
	md5 = models.CharField(max_length=50, blank=True, null=True)
	
	def path(self):
		return settings.MEDIA_ROOT + '640/' + self.md5 + '.jpg'
	
	def url(self):
		return settings.MEDIA_URL + '640/' + self.md5 + '.jpg'
			
	def resize(self):
		size = 640,640
		try:
			img = Image.open(self.image)
			md5sum = hashlib.md5(img.tostring()).hexdigest()
			self.md5 = md5sum		
			
			img = ImageOps.fit(img, size, Image.ANTIALIAS, 0, (0.5,0.5))
			img.save(self.path(), "JPEG")
		except IOError:
			print "Cannot create thumbnail for", original

	

