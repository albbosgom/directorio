from mainapp.models import Categoria, Webpage
from django.contrib import admin
from tags_input import admin as tags_input_admin




class WebpageAdmin(tags_input_admin.TagsInputAdmin):
    list_display = (
        'pk',
        'titulo',
    )
    search_fields = ('titulo',)
admin.site.register(Categoria)
admin.site.register(Webpage, WebpageAdmin)