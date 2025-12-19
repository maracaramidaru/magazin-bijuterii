from django.contrib.sitemaps import Sitemap, GenericSitemap
from django.urls import reverse
from .models import Produs

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["index", "despre", "contact", "produse"]

    def location(self, item):
        return reverse(item)

info_produse = {
    "queryset": Produs.objects.all(),
    'date_field': 'data_adaugarii', 
}
