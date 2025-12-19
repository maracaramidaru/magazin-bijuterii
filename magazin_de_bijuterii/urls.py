from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"), 
    path("info/", views.info, name="info"),
    path("baza/", views.baza, name="baza"),
    path("exemplu/", views.exemplu, name="exemplu"),
    path("test-accesare/", views.test_accesare, name="test_accesare"),
    path("log/", views.log, name="log"), 
    path('despre/', views.despre, name='despre'),
    path('in-lucru/', views.in_lucru, name='in_lucru'),
    path('produse/', views.produse, name='produse'),
    #path('produse/<int:produs_id>/', views.produs_detaliu, name='produs_detaliu'),
    path('produse/<str:categorie_nume>/', views.produse_categorie, name='produse_categorie'),
    path('contact/', views.contact, name='contact'),
    path('adauga_produs/', views.adauga_produs, name='adauga_produs'),
    path('cos/', views.vizualizare_cos, name='vizualizare_cos'),
    path('adauga_in_cos/<int:produs_id>/', views.adauga_in_cos, name='adauga_in_cos'),
    path('sterge_din_cos/<int:produs_id>/', views.sterge_din_cos, name='sterge_din_cos'),
    path('goleste_cos/', views.goleste_cos, name='goleste_cos'),
    path('inregistrare/', views.inregistrare_view, name='inregistrare'),
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/profil/', views.profil_view, name='profil'),
    path("confirma_mail/<str:cod>/", views.confirma_mail_view, name="confirma_mail"),
    path('promotii/', views.promotii_view, name='promotii'),
    path('produs/<int:produs_id>/', views.detalii_produs_view, name='detalii_produs'),
    path("interzis/", views.interzis_view, name="interzis"),
    path('logtest/', views.test_logging, name='test_logging'),


]
