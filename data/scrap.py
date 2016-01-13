# -*- encoding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import unicodedata
import os

print "Espere unos segundos para la creación del fichero yaml necesario para importar la base de datos"
def setUp():
    lstDir = os.walk("./")
    for root, dirs,files in lstDir:
        for fichero in files:
            (nombreFichero, extension) = os.path.splitext(fichero)
            if(extension != ".py" and extension != ".yaml"):
                os.remove(nombreFichero)
            elif(extension == ".yaml"):
                os.remove(nombreFichero+extension)
                
setUp()

def cleanUp():
    lstDir = os.walk("./")
    for root, dirs,files in lstDir:
        for fichero in files:
            (nombreFichero, extension) = os.path.splitext(fichero)
            if(extension != ".py" and extension != ".yaml"):
                os.remove(nombreFichero)

f = urllib2.urlopen("http://www.googledirectorio.com/")
f2 = open("webs", "w")
f2.writelines(f)
f.close()
f2 = open("webs","r")
html = f2.read()
soup = BeautifulSoup(html, 'html.parser')

split_tag = soup.find("table")
#print split_tag

all_category =[]
def extraerTags(): 
    for cate in split_tag.stripped_strings:
        if (cate != 'Directorios'):
            if (cate != 'Internet'):
                if (cate != 'Personales'):
                    if (cate != 'Traductor'):
                        if (cate != 'YouTube'):
                            if (cate != 'Otras Webs'):
                                all_category.append(cate)

extraerTags()
#print all_category

def crearArchivoTags():
    f3 = open("u'tags", "w")
    for cate in all_category:
        if cate == 'Viajes y Turismo':
            f3.write(cate)
        else:
            f3.write(cate + '\n')
    f3.close()
crearArchivoTags()

def extracInformacion():
    for cate in all_category:
        cate = cate.replace(" ","-")
        f = urllib2.urlopen("http://www.googledirectorio.com/"+cate+"/")
        f2 = open("u'"+cate+"", "w")
        f2.writelines(f)
        f.close()
    f2.close()     
extracInformacion()

def scrapInformacion():
    for cate in all_category:
        cate = cate.replace(" ","-")
        f2 = open("u'"+cate+"","r")
        html = f2.read()
        soup = BeautifulSoup(html, 'html.parser')
        
        split_web = soup.find("div",id="main2")
        
        titulos=[]
        enlaces=[]
        descripcion=[]
        descripcionaux=[]
        
        
        
        for title in split_web.find_all('a', target="_blank"):
            title = title.get_text()
            title = title = unicodedata.normalize('NFD', title).encode('ascii', 'ignore')
            title = title.replace(":"," ->")
            titulos.append(title)
        #print len(titulos)
        
        for link in split_web.find_all('a', target="_blank"):
            enlaces.append(link.get('href'))
        #print len(enlaces)
        
        
        for description in split_web.find_all('p'):
            description = description.get_text()
            description = description = unicodedata.normalize('NFD', description).encode('ascii', 'ignore')
            descripcionaux.append(description)
            
        i = 1
        for word in descripcionaux:
            if i % 2 == 0:
                word = word.replace("\n"," ")
                word = word.replace("\r",". ")
                word = word.replace("  "," ")
                word = word.replace(".",". ")
                word = word.replace(":"," ->")
                descripcion.append(word)
            i +=1
        #print len(descripcion)
        
                 
        f3 = open("u'itemsAux", "a")
        cate = cate.replace("-"," ")
        for i in range(len(titulos)):
            if i == 0:
                f3.write('\n'+titulos[i]+'$$'+enlaces[i]+'$$'+descripcion[i]+'$$'+cate+ '\n')
            elif (cate == all_category[-1]) and (i==9):
                f3.write(titulos[i]+'$$'+enlaces[i]+'$$'+descripcion[i]+'$$'+cate)
            else:
                f3.write(titulos[i]+'$$'+enlaces[i]+'$$'+descripcion[i]+'$$'+cate+ '\n')
    f2.close()    
    f3.close()            
        
scrapInformacion()

def quitarLineasEnBlanco():
    f3 = open("u'itemsAux", "r")
    for line in f3.readlines():
        if len(line) > 1:
            f4 = open("u'items", "a")
            f4.write(line)
    f3.close()
    f4.close()
quitarLineasEnBlanco()

f2.close()

def Yaml(lineaweb,categoria,id,i,ac):

    f1 = open("u'items.yaml", "a")
    f1.write("- model: mainapp.Categoria"+"\n")
    f1.write("  pk: "+str(ac)+"\n")
    f1.write("  fields:"+"\n")
    f1.write("    nombre: "+categoria+"\n\n")
    f1.write("- model: mainapp.Webpage"+"\n")
    f1.write("  pk: "+str(i)+"\n")
    f1.write("  fields:"+"\n")
    f1.write("    titulo: "+lineaweb[0]+"\n")
    f1.write("    enlace: "+lineaweb[1]+"\n")
    f1.write("    usuario: 1"+"\n")
    f1.write("    descripcion: "+lineaweb[2]+"\n\n")  
    f1.write("- model: mainapp.WebpageCategoria"+"\n")
    f1.write("  pk: "+str(i)+"\n")
    f1.write("  fields:"+"\n")
    f1.write("    webpage: "+str(id)+"\n")
    f1.write("    categoria: "+str(ac)+"\n")
    f1.write("    puntuacion: 0"+"\n\n")
    f1.close()


def Yaml1(lineaweb, id,i):
    f1 = open("u'items.yaml", "a")
    f1.write("- model: mainapp.Webpage"+"\n")
    f1.write("  pk: "+str(i)+"\n")
    f1.write("  fields:"+"\n")
    f1.write("    titulo: "+lineaweb[0]+"\n")
    f1.write("    enlace: "+lineaweb[1]+"\n")
    f1.write("    usuario: 1"+"\n")
    f1.write("    descripcion: "+lineaweb[2]+"\n\n")  
    f1.write("- model: mainapp.WebpageCategoria"+"\n")
    f1.write("  pk: "+str(i)+"\n")
    f1.write("  fields:"+"\n")
    f1.write("    webpage: "+str(i)+"\n")
    f1.write("    categoria: "+str(id)+"\n")
    f1.write("    puntuacion: 0"+"\n\n")
    f1.close()



def crearYaml():
    i = 1
    id = 1
    acu = 0
    acuaux = 1
    relacion = {}
    f = open("u'items", "r")
    for line in f.readlines():
        line = line.strip().split('$$')
        cate = line[3]
        if relacion.get(cate) == None:
            acu +=1
            relacion[cate] = [id]
            Yaml(line,cate,id,id,acu)
            id +=1
        else:
            a = relacion[cate]
            ac = id
            id = acu
            Yaml1(line, id,i)
            id = ac +1
            
        
        i +=1
    f.close()
    cleanUp()  
    print "Archivo yaml creado satisfactoriamente"

crearYaml()

