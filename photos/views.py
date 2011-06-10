# coding=utf-8
# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.views import login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random

from models import *
from forms import PhotoForm, UserForm

import Image, ImageOps, ImageFilter
import filters



@login_required
def edit_profile(request):
	""" Edit profile view function. Saves or gets user form. """
	if request.method == 'POST':
		form = UserForm(request.POST)
		if form.is_valid():
			user = form.save()
			return HttpResponseRedirect('/profile/')
			
	user = request.user
	form = UserForm(instance=user)
	return render_to_response('registration/edit_profile.html', locals(), context_instance=RequestContext(request))

# -- DJANGO SOCIAL AUTH REGISTRATION
"""
from social_auth.signals import socialauth_registered

def new_users_handler(sender, user, response, details, **kwargs):
	print 'new_users_handler'
	print sender
	print user
	print response
	print details
	for key, value in kwargs:
		print "%s:%s" % key, value
	
	return HttpResponseRedirect('/social_auth/')

socialauth_registered.connect(new_users_handler, sender=None)	
"""	

@login_required
def upload(request):
	""" Upload view function. Saves new photos or display upload form. """
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
	""" Index page. Shows 5 random photos, also displays 'welcome' in a random language"""
	photos = get_random_item(Photo, count=5)
	welcome = random.choice([u'Salaam',u'Dobrodošli',u'Vítáme te',u'Velkommen',u'Welkom',u'Bienvenue',u'Wolkom',u'Willkommen',u'Aloha',u'Shalom',u'Benvenuto',u'Bem-vindo',u'Bienvenido',u'Välkommen',u'Mabuhay',u'Swaagatham',u'Merhaba'])
	return render_to_response('index.html', locals())

@login_required
def profile(request, user_id="", page=1):
	""" Profile page. shows the user's photos with pagination """
	user = None
	errors = []
	photos = []	
	show_upload_link = False
	
	if not user_id:
		user = request.user
	else:
		try:
			user = User.objects.get(id=user_id)
		except User.DoesNotExist:
			errors.append("User does not exist")
	
	if user:
		try:
			photo_list = Photo.objects.filter(user=user).order_by('-upload_date')
		except Photo.DoesNotExist:
			pass
		if not photo_list:
			error = "%s has not uploaded any photos yet." % user.username
			errors.append(error)
			if user == request.user:
				show_upload_link = True
				
	paginator = Paginator(photo_list, 3) # Show 25 contacts per page
	
	try:
		photos = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		photos = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		photos = paginator.page(paginator.num_pages)
		
	
	base_url = '/profile/' + str(user.id) + '/'	
	if request.is_ajax():
		return render_to_response('photolist.html', locals())		
	return render_to_response('profile.html', locals())
	
	
def view(request, photo_id):
	errors = []
	try:
		photo = Photo.objects.get(id=photo_id)
		owner = True if (photo.user == request.user) else False
	except Photo.DoesNotExist:
		errors.append('No such photo exists.')
	return render_to_response('view.html', locals(), context_instance=RequestContext(request))

@login_required	
def delete(request, photo_id):
	errors = []
	messages = []
	photo = None
	
	try:
		photo = Photo.objects.get(id=photo_id)
	except Photo.DoesNotExist:
		errors.append('No such photo exists.')
	if photo:	
		if (photo.user == request.user):
			photo.delete()
			messages.append('Photo deleted successfully.')
			return render_to_response('base.html', locals(), context_instance=RequestContext(request))
		else:
			errors.append('You don\'t have access to delete that photo.')
			
	return render_to_response('view.html', locals(), context_instance=RequestContext(request))


def details(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	return render_to_response('photo_details.html', locals(), context_instance=RequestContext(request))
	
def edit(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	edit = True
	return render_to_response('view.html', locals(), context_instance=RequestContext(request))

def browse(request, filter=None, page=1):
	photos = []
	errors = []
	objects_per_page = 6

	if filter == "popular":
		filter_sql = "-views"
		title = "POPULAR PHOTOS"
	else:
		filter = "latest"
		filter_sql = "-upload_date"
		title = "LATEST PHOTOS"
		
	try:
		photos_list = Photo.objects.order_by(filter_sql)
	except Photo.DoesNotExist:
		errors.append('No photos to display.')
		
	paginator = Paginator(photos_list, objects_per_page) # Show 25 contacts per page
	
	try:
		photos = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		photos = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		photos = paginator.page(paginator.num_pages)
	
	base_url = '/browse/' + filter + '/'	
	if request.is_ajax():
		return render_to_response('photolist.html', locals())
	return render_to_response('browse.html', locals())
	


@login_required
def apply_filter(request, photo_id, operation='invert'):
	photo = Photo.objects.get(id=photo_id)
	if request.user != photo.user:
		errors = []
		errors.append('You haven\'t got permission to edit that photo.')
		return render_to_response('view.html', locals(), context_instance=RequestContext(request))

	
	if operation == 'revert': 
		return revert(request, photo_id)
		

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
	if operation == 'halftone': 
		img = filters.halftone(img)
	img.save(photo.path(), 'JPEG')
	
	photo.filtered = True
	photo.filter_used = operation
	photo.save()
	photo.generate_thumb()
	
	if request.is_ajax():
		return HttpResponse(photo.url())

	return HttpResponseRedirect('/edit/%s/' % photo.id)
	
def revert(request, photo_id):
	photo = Photo.objects.get(id=photo_id)
	photo.resize()
	photo.filtered = False
	photo.save()
	photo.generate_thumb()

	if request.is_ajax():
		return HttpResponse(photo.url())
	return HttpResponseRedirect('/view/%s/' % photo.id)