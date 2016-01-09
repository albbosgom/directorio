# Create your views here.
from django.shortcuts import render_to_response
from mainapp.models import Webpage
from mainapp.forms import WebForm
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from selenium import webdriver
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
    browser = webdriver.PhantomJS(executable_path=RUTA_PROYECTO+'\phantomjs.exe')
    browser.set_window_size(800, 600)
    capturas = []
    for webpage in webpages:
        browser.get(webpage.enlace)
        capturas.append((browser.get_screenshot_as_base64()))
    browser.quit()    
    return my_render(request, 'webpage.html', list=webpages)

def nuevaWeb(request):
    if request.method == 'POST':
        formulario = WebForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect('/')
    else:
        formulario = WebForm()
    return my_render(request, 'webform.html', formulario=formulario)
