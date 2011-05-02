# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from models import Photo
from forms import PhotoForm

import Image, ImageOps, ImageFilter

def upload(request):
	if request.method == 'POST':
		form = PhotoForm(request.POST, request.FILES)
		if form.is_valid():
			# handle_uploaded_file(request.FILES['image'])
			form.instance.resize()
			photo = form.save()
			return HttpResponseRedirect('/photos/view/%s/' % photo.id)
		
	else:
		form = PhotoForm()
	return render_to_response('upload.html', locals(), context_instance=RequestContext(request))
	
	
def view(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	return render_to_response('view.html', locals(), context_instance=RequestContext(request))

def apply_filter(request, photo_id, operation='invert'):
	photo = Photo.objects.get(id=photo_id)
	
	img = Image.open(photo.path())
	
	if operation == 'invert': 
		img = ImageOps.invert(img)
	elif operation == 'auto_contrast':
		img = ImageOps.autocontrast(img, 0.5)
	elif operation == 'posterize':
		img = ImageOps.posterize(img, 2)
	elif operation == 'median':
		img = img.filter(ImageFilter.MedianFilter())
	elif operation == 'bluify':
		img = ImageOps.colorize(ImageOps.grayscale(img), (0,0,0), (64,128,255))
		
	img.save(photo.path(), 'JPEG')
	
	return HttpResponseRedirect('/photos/view/%s/' % photo.id)
	
def revert(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	photo.resize()
	photo.save()
	
	return HttpResponseRedirect('/photos/view/%s/' % photo.id)