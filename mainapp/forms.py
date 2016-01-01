#encoding:utf-8 
from django.forms import ModelForm
from django import forms
from mainapp.models import Webpage

class WebForm(ModelForm):
    class Meta:
        model = Webpage
    