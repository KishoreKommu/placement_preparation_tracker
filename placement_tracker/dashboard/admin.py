from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = ('name', 'positions', 'skillset')
    

    search_fields = ('name', 'skillset')
    
    list_filter = ('positions',)