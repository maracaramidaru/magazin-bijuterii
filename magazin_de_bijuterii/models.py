# magazin_bijuterii/models.py
from django.db import models
from urllib.parse import urlparse, parse_qsl

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