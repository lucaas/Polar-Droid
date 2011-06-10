from django import forms
from models import Photo
from polardroid import settings
from django.contrib.admin.models import User

class PhotoForm(forms.ModelForm):
	class Meta:
		model = Photo
		exclude = 'md5, user, filtered, filter_used, exif, views'
		widgets = { 'image': forms.FileInput(attrs={'size':100}), }
		
class UserForm(forms.ModelForm):
	class Meta:
		model = User
		exclude = 'password, is_staff, is_active, is_superuser, last_login, date_joined, groups, user_permissions'