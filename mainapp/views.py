#encoding:utf-8
# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from mainapp.models import Webpage, WebpageCategoria, WebpageCategoriaPuntuacion, Categoria
from mainapp.forms import WebForm, CategoriasForm, EtiquetaForm
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from selenium import webdriver
from pattern.vector import Document
from pattern.web import plaintext
import urllib2
import os

RUTA_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Helper method to avoid repetitive template code
def my_render(request, template, **kwargs):
    return render_to_response(template, kwargs, context_instance=RequestContext(request))

def home(request):
    return my_render(request, 'home.html')

def appLogin(request):
    if request.method=='POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid:
            username = request.POST['username']
            password = request.POST['password']
            access = authenticate(username=username, password=password)
            if access is not None:
                if access.is_active:
                    login(request, access)
                    return HttpResponseRedirect('/')
    else:
        form = AuthenticationForm()
    return my_render(request, 'login.html', form=form)

def appLogout(request):
    logout(request)
    return HttpResponseRedirect('/')

def appRegistro(request):
    if request.method=='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid:
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = UserCreationForm()
    return my_render(request, 'registro.html', form=form)

def allPages(request):
    webpage_list = Webpage.objects.all()
    paginator = Paginator(webpage_list, 10)
    page = request.GET.get('page')
    try:
        webpages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        webpages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        webpages = paginator.page(paginator.num_pages)
    return my_render(request, 'webpage.html', list=webpages)

@login_required
def nuevaWeb(request):
    if request.method == 'POST':
        formulario = WebForm(request.POST, request.FILES)
        if formulario.is_valid():
            web = formulario.save(commit=False)
            web.usuario = request.user
            web.save()
            formulario.save_m2m()
            return HttpResponseRedirect('/')
    else:
        formulario = WebForm()
    return my_render(request, 'webform.html', formulario=formulario)

def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    
    url = urllib2.urlopen(cat_id).read()
    d = Document(plaintext(url),language="es",  stopwords = False)
    keywords = d.keywords(top=5)
    likes = ""
    for keyword in keywords:
        likes+=keyword[1]+","
    return HttpResponse(likes)

def parametros_normalizacion(web):
    """
    Esta función calcula los parámetros de normalización de las puntuaciones de las categorías de una web
    para trasladarlas al rango 0..5.
    """
    from django.db import models
    r = WebpageCategoria.objects.filter(webpage=web).aggregate(models.Min('puntuacion'), models.Max('puntuacion'), models.Avg('puntuacion'))
    rmin,rmax,ravg = r['puntuacion__min'],r['puntuacion__max'],r['puntuacion__avg']
    if (rmax-rmin)==0:
        return {'bias': 5.0 if rmax>0 else (3.0 if rmax==0 else 0.0), 'scale': 0.0, 'mean': ravg}
    ret = {'bias':-rmin, 'scale':5.0/(rmax-rmin)}
    ret['mean'] = (ravg+ret['bias'])*ret['scale']
    return ret

def normaliza(param, val):
    """Esta función normaliza la puntuación de una categoría al rango 0..5 y resta la media de las puntuaciones."""
    return (val+param['bias'])*param['scale']-param['mean']

def calcula_similitud(web1, web2, categorias):
    """
    Esta función calcula el coeficiente de similitud de Pearson de dos webs.
    """
    from math import sqrt
    norm1,norm2 = parametros_normalizacion(web1),parametros_normalizacion(web2)
    numera,denomina_a,denomina_b = 0,0,0
    for cat in categorias:
        s1 = normaliza(norm1, WebpageCategoria.objects.get(webpage=web1,categoria=cat).puntuacion)
        s2 = normaliza(norm2, WebpageCategoria.objects.get(webpage=web2,categoria=cat).puntuacion)
        numera += s1*s2
        denomina_a += s1*s1
        denomina_b += s2*s2
    if denomina_a==0 or denomina_b==0:
        return 0
    return numera / sqrt(denomina_a*denomina_b)

def calcula_corrector(web1, web2, categorias):
    """
    Esta función calcula el coeficiente de corrección de una web, que es el número de categorías con puntuación
    igual o superior a cero comunes a las dos webs.
    """
    nCatBuenas = WebpageCategoria.objects.filter(categoria__in=categorias,webpage__in=[web1,web2],puntuacion__gte=0).count()
    return float(nCatBuenas+1)

def calcula_coef(d,max_corrector):
    """
    Esta función corrige el coeficiente de similaridad utilizando el coeficiente corrector.
    Se emplea la raíz cuadrada para suavizar el efecto del corrector en webs con número de
    categorías apropiadas comunes similares.
    """
    from math import sqrt
    fcorr = sqrt(d['corr']/max_corrector)
    return d['sim']*fcorr

def calculaProximos(webpage,N=5):
    webs = []
    max_corrector = 0
    for obj in Webpage.objects.all():
        if obj==webpage:
            continue
        # Calcular las categorías comunes con la web actual
        cate = Categoria.objects.filter(webpage=webpage).filter(webpage=obj)
        if not cate: # Ignorar la web si no hay categorías comunes
            continue
        # Calcular el coeficiente de similaridad y el de corrección
        similitud,corrector = calcula_similitud(webpage, obj, cate),calcula_corrector(webpage, obj, cate)
        max_corrector = max(max_corrector, corrector)
        # Añadir web a la lista de webs
        webs.append({"web":obj, "sim":similitud, "corr":corrector})
    # Si el coeficiente de corrección máximo es cero, significa que ninguna categoría común con otras webs describe bien a la web
    if max_corrector==0:
        return []
    # Calcular el coeficiente de similaridad final utilizando el factor corrector
    for d in webs:
        d['coef'] = calcula_coef(d, max_corrector)
    # Devolver las N webs con coeficiente mayor
    webs = sorted(webs, key=lambda k:k['coef'], reverse=True)
    return [(a['coef'],a['web']) for a in webs[0:N]]

def verWeb(request, webpage_id):
    webpage = get_object_or_404(Webpage, pk=webpage_id)
    categolist = Paginator(WebpageCategoria.objects.filter(webpage=webpage, puntuacion__gte=0).order_by('-puntuacion'), 5).page(1)
    browser = webdriver.PhantomJS(executable_path=RUTA_PROYECTO+'\phantomjs.exe')
    browser.set_window_size(800, 600)
    browser.get(webpage.enlace)
    captura = browser.get_screenshot_as_base64()
    browser.quit()
    related = calculaProximos(webpage)
    return my_render(request, 'webpageview.html', webpage=webpage, captura=captura, categolist=categolist, related=related, pk=webpage_id)

@login_required
def tagVote_List(request, webpage_id):
    webpage = get_object_or_404(Webpage, pk=webpage_id)
    if request.method=='POST':
        formulario = EtiquetaForm(request.POST)
        if formulario.is_valid():
            nombrecat = formulario.cleaned_data['etiqueta']
            try:
                categoria = Categoria.objects.get(nombre = nombrecat)
            except Categoria.DoesNotExist:
                categoria = Categoria.objects.create(nombre = nombrecat)
                categoria.save()
            webpage.categoria.add(categoria)
            webpage.save()
            formulario = EtiquetaForm()
    else:
        formulario = EtiquetaForm()
    taglist = WebpageCategoria.objects.filter(webpage=webpage).order_by('-puntuacion')
    votes = WebpageCategoriaPuntuacion.objects.filter(webpage=webpage,usuario=request.user)
    themap = {}
    for vote in votes:
        themap[vote.categoria.pk] = vote.puntuacion
    return my_render(request, 'tagvote.html', webpage=webpage, list=taglist, votes=themap, pk=webpage_id, form=formulario)

@login_required
def tagVote_VoteYes(request, webpage_id, categoria_id):
    webpage = get_object_or_404(Webpage, pk=webpage_id)
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    o = WebpageCategoriaPuntuacion.objects.create(webpage=webpage, categoria=categoria, usuario=request.user, puntuacion=+1)
    o.save()
    return HttpResponseRedirect('/directorio/%s/etiquetas/' % (webpage_id,))

@login_required
def tagVote_VoteNo(request, webpage_id, categoria_id):
    webpage = get_object_or_404(Webpage, pk=webpage_id)
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    o = WebpageCategoriaPuntuacion.objects.create(webpage=webpage, categoria=categoria, usuario=request.user, puntuacion=-1)
    o.save()
    return HttpResponseRedirect('/directorio/%s/etiquetas/' % (webpage_id,))

@login_required
def tagVote_VoteDel(request, webpage_id, categoria_id):
    webpage = get_object_or_404(Webpage, pk=webpage_id)
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    o = WebpageCategoriaPuntuacion.objects.get(webpage=webpage, categoria=categoria, usuario=request.user)
    o.delete()
    return HttpResponseRedirect('/directorio/%s/etiquetas/' % (webpage_id,))

def lista_webs(request,categorias):
    webpage_list = Webpage.objects
    for categoria in categorias:
        webpage_list = webpage_list.filter(categoria=categoria)
    paginator = Paginator(webpage_list, 10)
    page = request.GET.get('page')
    try:
        webpages = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        webpages = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        webpages = paginator.page(paginator.num_pages)
    return my_render(request, 'webpage.html', list=webpages)

def BuscadorWebsPorCategoria(request):
    if request.method=='POST':
        formulario = CategoriasForm(request.POST)
        if formulario.is_valid():
            nombrecat = formulario.cleaned_data['categoria']
            nombrecat = [a.strip() for a in nombrecat.split(',')]
            categorias = Categoria.objects.filter(nombre__in = nombrecat)
            if categorias:
                return lista_webs(request,categorias)
    else:
        formulario = CategoriasForm()
    return my_render(request,'searchWebsForm.html', formulario=formulario)
