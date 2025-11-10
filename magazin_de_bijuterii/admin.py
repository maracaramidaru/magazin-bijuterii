from django.contrib import admin
from .models import Produs, Categorie, Material, Brand, Dimensiune, Imagine


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    search_fields = ['nume', 'descriere']  
    list_display = ['nume', 'descriere'] 
    ordering = ['nume'] 
    list_per_page = 5  


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    search_fields = ['nume', 'descriere']
    list_display = ['nume', 'tara_origine', 'descriere']
    list_filter = ['tara_origine']  
    ordering = ['nume']
    list_per_page = 5


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    search_fields = ['descriere']
    list_display = ['get_material_display', 'descriere']
    ordering = ['material']
    list_per_page = 5


@admin.register(Dimensiune)
class DimensiuneAdmin(admin.ModelAdmin):
    list_display = ['marime', 'greutate']
    search_fields = ['marime', 'greutate']
    ordering = ['marime']
    list_per_page = 5


class ImagineInline(admin.TabularInline):
    model = Imagine
    extra = 1


@admin.register(Produs)
class ProdusAdmin(admin.ModelAdmin):
    list_display = ('nume', 'pret', 'disponibilitate', 'categorie', 'brand', 'data_adaugarii')
    list_filter = ('categorie', 'brand', 'disponibilitate')
    search_fields = ('nume', 'descriere')
    ordering = ('-pret',)
    list_per_page = 5
    inlines = [ImagineInline]
    fieldsets = (
        ('Informații de bază', {   
            'fields': ('nume', 'pret', 'categorie', 'brand'),
        }),
        ('Detalii opționale', {    
            'classes': ('collapse',),  
            'fields': ('descriere', 'disponibilitate', 'material', 'dimensiune'),
            'description': 'Aici poți adăuga detalii opționale despre produs.',
        }),
    )

admin.site.site_header = "Magazin de Bijuterii — Panou de Administrare"
admin.site.site_title = "Administrare Magazin Bijuterii"
admin.site.index_title = "Bun venit în zona de administrare"

# Register your models here.
