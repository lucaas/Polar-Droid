# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from models import Photo
from forms import PhotoForm

import Image, ImageOps, ImageFilter
import filters

@login_required
def upload(request):
	if request.method == 'POST':
		form = PhotoForm(request.POST, request.FILES)
		if form.is_valid():
			# handle_uploaded_file(request.FILES['image'])
			photo = form.save(commit=False)
			photo.create(request.user)

			return HttpResponseRedirect('/view/%s/' % photo.id)
		
	else:
		form = PhotoForm()
	return render_to_response('upload.html', locals(), context_instance=RequestContext(request))
	
def index(request):
	return render_to_response('index.html', locals())

@login_required
def profile(request, user_id=""):

	user = None
	errors = []
	photos = []	
	
	if not user_id:
		user = request.user
	else:
		try:
			user = User.objects.get(id=user_id)
		except User.DoesNotExist:
			errors.append("User does not exist")
	
	if user:
		try:
			photos = Photo.objects.filter(user=user)
		except Photo.DoesNotExist:
			pass
		if not photos:
			str = "%s has not uploaded any photos yet." % user.username
			errors.append(str)	
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
	
	img = Image.open(photo.original_path())
	
	if operation == 'lomo': 
		img = filters.lomo(img)
	if operation == 'agfa': 
		img = filters.agfa(img)
	if operation == 'bw': 
		img = filters.bw(img)
	if operation == 'bw2': 
		img = filters.bw2(img)
	if operation == 'army': 
		img = filters.army(img)
	if operation == 'cyan_glow': 
		img = filters.cyan_glow(img)	
	if operation == 'oldie': 
		img = filters.oldie(img)
	img.save(photo.path(), 'JPEG')
	
	photo.filtered = True
	photo.filter_used = operation
	photo.save()
	
	return HttpResponseRedirect('/edit/%s/' % photo.id)
	
def revert(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	photo.resize()
	photo.filtered = False
	photo.save()
	
	return HttpResponseRedirect('/view/%s/' % photo.id)