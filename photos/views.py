# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from models import Photo
from forms import PhotoForm

import Image, ImageOps, ImageFilter

@login_required
def upload(request):
	if request.method == 'POST':
		form = PhotoForm(request.POST, request.FILES)
		if form.is_valid():
			# handle_uploaded_file(request.FILES['image'])
			form.instance.resize()
			photo = form.save()
			return HttpResponseRedirect('/view/%s/' % photo.id)
		
	else:
		form = PhotoForm()
	return render_to_response('upload.html', locals(), context_instance=RequestContext(request))

@login_required
def profile(request):
	user = request.user
	fields = [(field.name, field.value_to_string(user)) for field in User._meta.fields]
	return render_to_response('profile.html', locals())
	
	
def view(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	return render_to_response('view.html', locals(), context_instance=RequestContext(request))

def edit(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	edit = True
	return render_to_response('view.html', locals(), context_instance=RequestContext(request))

def browse(request):
	photos = []
	errors = []
	try:
		photos = Photo.objects.all()
	except Photo.DoesNotExist:
		errors.append('No photos in database.')
	if not photos:
		errors.append('No photos in database.')
	return render_to_response('browse.html', locals())


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
	
	return HttpResponseRedirect('/view/%s/' % photo.id)
	
def revert(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	photo.resize()
	photo.save()
	
	return HttpResponseRedirect('/view/%s/' % photo.id)