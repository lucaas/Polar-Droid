from django.db import models
from django.db.models import Max
from django.contrib.admin.models import User
from django.contrib import admin
from polardroid import settings

import Image, ImageOps
from PIL.ExifTags import TAGS

import datetime, hashlib, random


class Photo(models.Model):
	""" Photo model, contains image paths and various associated info. """
	title = models.CharField(max_length=50)
	image = models.ImageField(upload_to="original")
	md5 = models.CharField(max_length=50, blank=True, null=True)
	user = models.ForeignKey(User)
	filtered = models.BooleanField(default=False)
	filter_used = models.CharField(max_length=50, blank=True, default="")
	exif = models.OneToOneField('Exif', null=True, related_name="photo")
	upload_date = models.DateTimeField(auto_now_add=True)
	views = models.PositiveIntegerField(default=0)
	

	def __unicode__(self):
		return self.title
			
		
	def views_add(self):
		Photo.objects.filter(id=self.id).update(views = models.F('views') + 1)
		return self.views + 1
		
	def original_path(self):
		return settings.MEDIA_ROOT + '640/' + self.md5 + '.png'
	
	def path(self):
		return settings.MEDIA_ROOT + 'filtered/' + self.md5 + '.jpg'
	
	def thumb_path(self):
		return settings.MEDIA_ROOT + 'thumbs/' + self.md5 + '.jpg'
	
	def thumb_url(self):
		return settings.MEDIA_URL + 'thumbs/' + self.md5 + '.jpg'
		
	def url(self):
		if self.filtered:
			return settings.MEDIA_URL + 'filtered/' + self.md5 + '.jpg'
		else:
			return settings.MEDIA_URL + '640/' + self.md5 + '.png'
	
	def create(self, user):
		# Set user
		self.user = user
		
		# generate MD5
		md5sum = hashlib.md5(repr(self.image) + repr(datetime.datetime.now())).hexdigest()
		self.md5 = md5sum	
		
		img = Image.open(self.image)
		
		# Get and handle exif
		exif = Exif()
		if exif.get_exif(img):
			self.exif = exif
				
		# resize image
		orientation = exif.orientation if exif.orientation else None
		self.resize(img, orientation=orientation)
		self.save()
		self.generate_thumb()
			
	def generate_thumb(self):
		size = (320,320)
		img = Image.open(self.path()) if self.filtered else Image.open(self.original_path())
		img.thumbnail(size, Image.ANTIALIAS)
		img.save(self.thumb_path(), "JPEG")
	
		
	def resize(self, img=None, orientation=None):
		size = 640,640
		try:
			if not img:
				img = Image.open(self.image)
				
			# Rotate/Flip image according to orientation
			if orientation:
				if orientation == 1: 
					pass
				elif orientation == 2: 
					img = img.transpose(Image.FLIP_LEFT_RIGHT)
				elif orientation == 3: 
					img = img.transpose(Image.ROTATE_180)                
				elif orientation == 4: 
					img = img.transpose(Image.FLIP_TOP_BOTTOM) 
				elif orientation == 5: 
					img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
				elif orientation == 6: 
					img = img.transpose(Image.ROTATE_270)
				elif orientation == 7: 
					img = img.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)
				elif orientation == 8: 
					img = img.transpose(Image.ROTATE_90) 
				
			img = ImageOps.fit(img, size, Image.ANTIALIAS, 0, (0.5,0.5))
			img.save(self.original_path(), "PNG")

		except IOError:
			print "Cannot create resized image for ", self.image

				
admin.site.register(Photo)	

# Additional model methods used...


import os                    
from django.db.models.signals import post_delete

def remove_images(sender, instance, **kwargs):
	try:
		os.remove( instance.original_path()	)
		os.remove( instance.thumb_path() )
		os.remove( instance.path() )
	except (IOError, OSError):
		pass
		
post_delete.connect(remove_images, sender=Photo)


def get_random_item(model, max_id=None, count=1):
	number = 5
	ids = model.objects.all().values_list('id', flat=True)
	amount = min(len(ids), number)
	picked_ids = random.sample(ids, amount)
	return model.objects.filter(id__in=picked_ids)
	


class Exif(models.Model):
	""" model for exif metadata such as camera model and geolocation """
	lat = models.FloatField(blank=True, null=True)
	long = models.FloatField(blank=True, null=True)
	camera = models.CharField(max_length=100, blank=True, null=True)
	shot_date = models.DateTimeField(blank=True, null=True)
	flash = models.NullBooleanField()
	orientation = models.PositiveSmallIntegerField(blank=True, null=True)
	
	def get_exif(self, img):
		result = {}
		ret = {}
		
		try:
			info = img._getexif()
		except AttributeError:
			return False
	
			
		if info:
			for tag, value in info.items():
				decoded = TAGS.get(tag, tag)
				ret[decoded] = value
			
			if not ret:
				return False
			"""
			print "---------"
			print "EXIF INFO: "
			print ""
			print ret
			print ""
			"""
			if 'GPSInfo' in ret and ret['GPSInfo']:
				NS = 1 if (ret['GPSInfo'][1] == 'N') else -1
				EW = 1 if (ret['GPSInfo'][3] == 'E') else -1
				self.lat = NS * (float(ret['GPSInfo'][2][0][0]) / ret['GPSInfo'][2][0][1] + float(ret['GPSInfo'][2][1][0])/ret['GPSInfo'][2][1][1]/60.0)
				self.long = EW * (float(ret['GPSInfo'][4][0][0]) / ret['GPSInfo'][4][0][1] + float(ret['GPSInfo'][4][1][0])/ret['GPSInfo'][4][1][1]/60.0)
			
			if 'Model' in ret and ret['Model']:
				self.camera = ret['Model']
			
			try:
				if 'DateTime' in ret and ret['DateTime']:
					self.shot_date = datetime.datetime.strptime(ret['DateTime'], "%Y:%m:%d %H:%M:%S")
				elif 'DateTimeOriginal' in ret and ret['DateTimeOriginal']:
					self.shot_date = datetime.datetime.strptime(ret['DateTimeOriginal'], "%Y:%m:%d %H:%M:%S")
			except ValidationError:
				pass
			
			if 'Flash' in ret and ret['Flash']:
				flash = ret['Flash']
				if flash in (1,7,9,13,15,25,29,31,65,69,71,73,77,79,89,93,95):
					self.flash = True
				else:
					self.flash = False
					
			if 'Orientation' in ret and ret['Orientation']:
				self.orientation = ret['Orientation']
				
		else:
			return False
			
		
		self.save()
		return True
		
admin.site.register(Exif)	
