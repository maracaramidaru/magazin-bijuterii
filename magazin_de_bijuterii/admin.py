from django.contrib import admin
from .models import Produs, Categorie, Material, Brand, Dimensiune, Imagine,Vizualizare
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import Promotie
from .forms import PromotieForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

class PromotieAdmin(admin.ModelAdmin):
    filter_horizontal = ("categorii",)

admin.site.register(Promotie, PromotieAdmin)

class VizualizareAdmin(admin.ModelAdmin):
    list_display = ('user', 'produs', 'data_vizualizare')
    search_fields = ('user__username', 'produs__nume')
    list_filter = ('data_vizualizare',)
    ordering = ('-data_vizualizare',)
    list_per_page = 10
admin.site.register(Vizualizare, VizualizareAdmin)
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ("Informații suplimentare", {
            "fields": ("telefon", "adresa", "oras", "data_nasterii", "gen", "blocat")
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informații suplimentare", {
            "fields": ("telefon", "adresa", "oras", "data_nasterii", "gen", "blocat")
        }),
    )

    list_display = ("username", "email", "first_name", "last_name", "blocat", "is_staff")

    def get_readonly_fields(self, request, obj=None):
      
        if request.user.groups.filter(name="Moderatori").exists():
            return [
                "username", "password", "is_superuser", "is_staff",
                "is_active", "groups", "user_permissions",
                "last_login", "date_joined"
            ]
        return super().get_readonly_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
       
        if request.user.groups.filter(name="Moderatori").exists():
            return (
                (None, {"fields": ("username", "password")}),
                ("Informații personale", {"fields": ("first_name", "last_name", "email")}),
                ("Informații suplimentare", {
                    "fields": ("telefon", "adresa", "oras", "data_nasterii", "gen", "blocat")
                }),
                ("Grupuri (doar vizualizare)", {"fields": ("groups",)}),
            )

        # SUPERUSER,STAFFaici adaug toate permisiunile și câmpurile is_staff,is_active
        fieldsets = super().get_fieldsets(request, obj)

        return fieldsets + (
            ("Permisiuni și grupuri", {
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
            }),
        )

admin.site.unregister(Group)

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):

    readonly_fields = ('users_in_group',)

    def users_in_group(self, obj):
        users = obj.user_set.all()
        if not users:
            return "Niciun utilizator în acest grup."

        return ", ".join([user.username for user in users])

    users_in_group.short_description = "Utilizatori în acest grup"

    def get_fieldsets(self, request, obj=None):
       
        fieldsets = list(super().get_fieldsets(request, obj))

        # Adaug secțiunea ca un nou tuplu în listă
        fieldsets.append(
            ("Utilizatori", {"fields": ("users_in_group",)})
        )

        return fieldsets


    
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
