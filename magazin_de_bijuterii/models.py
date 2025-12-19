
from django.db import models
from urllib.parse import urlparse, parse_qsl
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings 
from django.urls import reverse

GEN_CHOICES = [
    ('M', 'Masculin'),
    ('F', 'Feminin'),
]

class CustomUser(AbstractUser):
    telefon = models.CharField(max_length=15)
    adresa = models.CharField(max_length=255)
    oras = models.CharField(max_length=100)
    data_nasterii = models.DateField()
    gen = models.CharField(max_length=10, choices=GEN_CHOICES)
    blocat = models.BooleanField(default=False)
    cod = models.CharField(max_length=100, null=True, blank=True)
    email_confirmat = models.BooleanField(default=False)
    REQUIRED_FIELDS = ['email', 'telefon', 'adresa', 'oras', 'data_nasterii', 'gen']

    def __str__(self):
        return self.username
    
class Accesare(models.Model):
    ip_client = models.GenericIPAddressField(null=True, blank=True)
    url = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def lista_parametri(self):
        parsed = urlparse(self.url)
        pairs = parse_qsl(parsed.query, keep_blank_values=True)
        result = []
        for k, v in pairs:
            result.append((k, v if v != '' else None))
        return result

    def url_complet(self):
        return self.url

    def data(self, fmt=None):
        if fmt is None:
            return self.timestamp
        return self.timestamp.strftime(fmt)

    def pagina(self):
        parsed = urlparse(self.url)
        return parsed.path or '/'
    
    
#modelele
class Categorie(models.Model):
    nume = models.CharField(max_length=100)
    descriere = models.TextField()
    culoare = models.CharField(max_length=20, default="#cccccc")  
    icon = models.CharField(max_length=50, blank=True, null=True)  

    def __str__(self):
        return self.nume


class Brand(models.Model):
    nume = models.CharField(max_length=100)
    tara_origine = models.CharField(max_length=100)
    descriere = models.TextField()

    def __str__(self):
        return self.nume


class Material(models.Model):
    class MaterialChoices(models.IntegerChoices):
        AUR = 1, 'Aur'
        ARGINT = 2, 'Argint'
        AUR_ALB = 3, 'Aur alb'
        AUR_ROZ = 4, 'Aur roz'

    material = models.IntegerField(
        choices=MaterialChoices.choices,
        default=MaterialChoices.ARGINT
    )
    descriere = models.TextField(blank=True)

    def __str__(self):
        return self.get_material_display()


class Dimensiune(models.Model):
    marime = models.DecimalField(max_digits=4, decimal_places=1)
    greutate = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.marime} cm / {self.greutate} g"


class Produs(models.Model):
    nume = models.CharField(max_length=100)
    descriere = models.TextField()
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilitate = models.BooleanField(default=True)
    data_adaugarii = models.DateField(auto_now_add=True)
    material = models.ManyToManyField(Material, related_name='produse')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produse')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='produse')
    dimensiune = models.ManyToManyField(Dimensiune, related_name='produse')

    def get_absolute_url(self):
        return reverse('detalii_produs', args=[self.id])
    def __str__(self):
        return self.nume
    
    class Meta:
        ordering = ['nume']
        indexes = [
            models.Index(fields=['pret']),
            models.Index(fields=['disponibilitate']),
        ]

    def disponibilitate_text(self):
        return "Disponibil" if self.disponibilitate else "Indisponibil"

class Imagine(models.Model):
    produs = models.ForeignKey(Produs, on_delete=models.CASCADE, related_name='imagini')
    url_imagine = models.URLField()
    descriere = models.TextField(blank=True)

    def __str__(self):
        return f"Imagine pentru {self.produs.nume}"
N = 5  
K = 3   

class Vizualizare(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    produs = models.ForeignKey(Produs, on_delete=models.CASCADE)
    data_vizualizare = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-data_vizualizare']  # cele mai noi primele


class Promotie(models.Model):
    nume = models.CharField(max_length=100)
    subiect = models.CharField(max_length=200)
    mesaj = models.TextField()
    data_creare = models.DateTimeField(default=timezone.now)
    data_expirare = models.DateField()
    
    reducere_procent = models.IntegerField(default=10)
    cod_cupon = models.CharField(max_length=50)
    categorii = models.ManyToManyField("Categorie")  

    def __str__(self):
        return self.nume