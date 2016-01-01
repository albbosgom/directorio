# Create your views here.
from django.shortcuts import render_to_response
from mainapp.models import Webpage
from mainapp.forms import WebForm
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from selenium import webdriver
import os

RUTA_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def home(request):
    return render_to_response('home.html')

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
    print RUTA_PROYECTO
    browser = webdriver.PhantomJS(executable_path=RUTA_PROYECTO+'\phantomjs.exe')
    augmenter = 
    browser.set_window_size(1280, 720)
    capturas = []
    for webpage in webpages:
        browser.get(webpage.enlace)
        capturas.append((browser.get_screenshot_as_base64()))  
    browser.quit()    
    return render_to_response('webpage.html', {'list':webpages, 'capturas':capturas})

def nuevaWeb(request):
    if request.method == 'POST':
        formulario = WebForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            return HttpResponseRedirect('/')
    else:
        formulario = WebForm()
    return render_to_response('webform.html', {'formulario':formulario}, context_instance= RequestContext(request))
        