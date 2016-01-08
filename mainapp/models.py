#encoding:utf-8
from django.db import models

# Create your models here.


class ReprModel(models.Model):
    def __repr__(self):
        return '<%s[%d]: %s>' % (
            self.__class__.__name__,
            self.pk or -1,
            self.name,
        )

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

class Categoria(ReprModel):
    nombre = models.CharField(max_length=50)
    def __unicode__(self):
        return self.nombre
    

class Webpage(ReprModel):
    titulo = models.CharField(max_length=100)
    enlace = models.URLField(verify_exists=True)
    categoria = models.ManyToManyField(Categoria)
    def __unicode__(self):
        return self.titulo
    