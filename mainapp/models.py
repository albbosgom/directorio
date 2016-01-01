#encoding:utf-8
from django.db import models

# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    def __unicode__(self):
        return self.nombre

class Webpage(models.Model):
    titulo = models.CharField(max_length=100)
    enlace = models.URLField(verify_exists=True)
    categorias = models.ManyToManyField(Categoria)
    def __unicode__(self):
        return self.titulo