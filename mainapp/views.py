# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from mainapp.models import Webpage, WebpageCategoria, WebpageCategoriaPuntuacion, Categoria
from mainapp.forms import WebForm
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from selenium import webdriver
from pattern.vector import Document
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
    paginator = Paginator(webpage_list, 2)
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
    context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    
    url = urllib2.urlopen(cat_id).read()
    d = Document(url, threshold = 1)
    keywords = d.keywords(top=5)
    likes = ""
    for keyword in keywords:
        likes +='<span class="tag"><span>'+keyword[1]+'</span><a href="#" title="Removing tag">x</a></span>'
    print likes
    return HttpResponse(likes)

def verWeb(request, webpage_id):
    webpage = get_object_or_404(Webpage, pk=webpage_id)
    categolist = Paginator(WebpageCategoria.objects.filter(webpage=webpage, puntuacion__gt=0).order_by('-puntuacion'), 5).page(1)
    browser = webdriver.PhantomJS(executable_path=RUTA_PROYECTO+'\phantomjs.exe')
    browser.set_window_size(800, 600)
    browser.get(webpage.enlace)
    captura = browser.get_screenshot_as_base64()
    browser.quit()
    return my_render(request, 'webpageview.html', webpage=webpage, captura=captura, categolist=categolist, pk=webpage_id)

@login_required
def tagVote_List(request, webpage_id):
    webpage = get_object_or_404(Webpage, pk=webpage_id)
    taglist = WebpageCategoria.objects.filter(webpage=webpage).order_by('-puntuacion')
    votes = WebpageCategoriaPuntuacion.objects.filter(webpage=webpage,usuario=request.user)
    themap = {}
    for vote in votes:
        themap[vote.categoria.pk] = vote.puntuacion
    return my_render(request, 'tagvote.html', webpage=webpage, list=taglist, votes=themap, pk=webpage_id)

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
