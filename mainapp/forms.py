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
        fields = ('titulo', 'enlace', 'descripcion', 'categoria')
        widgets = {
            'categoria': widgets.TagsInputWidget
        }
        
class CategoriasForm(forms.Form):
    categoria = forms.CharField(label="Categoría",help_text="Introduzca las categorías separadas por comas")

class EtiquetaForm(forms.Form):
    etiqueta = forms.CharField(label="Etiqueta",help_text="Introduzca la etiqueta a añadir")
    