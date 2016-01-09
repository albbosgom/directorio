#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User

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
    votos = models
    def __unicode__(self):
        return self.nombre
    

class Webpage(ReprModel):
    titulo = models.CharField(max_length=100)
    enlace = models.URLField()
    categoria = models.ManyToManyField(Categoria, through='WebpageCategoria')
    def __unicode__(self):
        return self.titulo
    
class WebpageCategoria(ReprModel):
    webpage = models.ForeignKey(Webpage)
    categoria = models.ForeignKey(Categoria)
    puntuacion = models.IntegerField(default=0) #Por favor mantener sincronizado con WebpageCategoriaPuntuacion
    def __unicode__(self):
        return u"<%s - %s>" % (self.webpage, self.categoria)
    class Meta:
        unique_together = ("webpage", "categoria")
        auto_created = True
    

class WebpageCategoriaPuntuacion(ReprModel):
    webpage = models.ForeignKey(Webpage)
    categoria = models.ForeignKey(Categoria)
    usuario = models.ForeignKey(User)
    puntuacion = models.SmallIntegerField(choices=((+1,'Apropiado'),(-1,'Inapropiado')))
    def __unicode__(self):
        return u"<%s - %s - %s>" % (self.webpage, self.categoria, self.usuario)
    def actualiza_puntuacion(self):
        wc = WebpageCategoria.objects.get(webpage=self.webpage,categoria=self.categoria)
        wc.puntuacion = WebpageCategoriaPuntuacion.objects.filter(webpage=self.webpage,categoria=self.categoria).aggregate(models.Sum('puntuacion'))["puntuacion__sum"] or 0
        wc.save()
    def delete(self, *args, **kwargs):
        super(ReprModel,self).delete(*args, **kwargs)
        self.actualiza_puntuacion()
    def save(self, *args, **kwargs):
        super(ReprModel,self).save(*args, **kwargs)
        self.actualiza_puntuacion()
    class Meta:
        unique_together = ("webpage", "categoria", "usuario")
