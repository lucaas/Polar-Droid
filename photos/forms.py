from django import forms
from models import Photo
from polardroid import settings


class PhotoForm(forms.ModelForm):
	class Meta:
		model = Photo
		exclude = 'md5, user'