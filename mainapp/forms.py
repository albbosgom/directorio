#encoding:utf-8 
from django.forms import ModelForm
from mainapp.models import Categoria
from django import forms
from mainapp.models import Webpage
from tags_input import widgets, fields


class WebForm(ModelForm):
    categoria = fields.TagsInputField(
        Categoria.objects.all(),
        create_missing=True,)
    class Meta:
        model = Webpage
        widgets = {
            'categoria': widgets.TagsInputWidget
        }