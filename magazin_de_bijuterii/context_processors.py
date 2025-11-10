from .models import Categorie

def categorii_globale(request):
    return {
        'categorii': Categorie.objects.all()
    }