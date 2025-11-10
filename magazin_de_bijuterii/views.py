from django.shortcuts import render,get_object_or_404, redirect
from .models import Produs, Categorie, Brand, Material, Dimensiune, Imagine
from datetime import datetime
from urllib.parse import urlparse
from django.http import HttpResponse
from .models import Accesare
from collections import Counter
from urllib.parse import urlparse
from django.core.paginator import Paginator
from .forms import ProduseFilterForm, ContactForm, ProdusForm
from django.contrib import messages
from django import forms
import os
import json
import time


def index(request):
    return HttpResponse("Bine ai venit la magazinul de bijuterii! Acesta este primul meu răspuns.")


def afis_data(parametru=None):
    zile_saptamana = ["Luni", "Marti", "Miercuri", "Joi", "Vineri", "Sambata", "Duminica"]
    luni_an = ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie",
               "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"]

    acum = datetime.now()
    zi_saptamana = zile_saptamana[acum.weekday()]
    zi_luna = acum.day
    luna = luni_an[acum.month - 1]
    an = acum.year
    ora = acum.strftime("%H:%M:%S")

    if parametru == "zi":
        return f"{zi_saptamana}, {zi_luna} {luna} {an}"
    elif parametru == "timp":
        return f"{ora}"
    else:
        return f"{zi_saptamana}, {zi_luna} {luna} {an}, {ora}"


def afis_template(request):
    return render(request, "articole/articole.html", {
        "titlu_tab": "Titlu fereastra",
        "titlu_articol": "Titlu afisat",
        "continut_articol": "Continut text"
    })

def info(request):
    param_data = request.GET.get('data', None)
    data_curenta = afis_data(param_data)

    ip = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR')
    full_url = request.build_absolute_uri()

    acces = Accesare.objects.create(
        ip_client=ip,
        url=full_url
    )

    data_formatata = acces.data("%Y-%m-%d %H:%M:%S")
    lista_parametri = acces.lista_parametri()
    nr_parametri = len(lista_parametri)

    context = {
        "data_curenta": data_curenta,
        "acces": acces,
        "data_formatata": data_formatata,
        "lista_parametri": lista_parametri,
        "nr_parametri": nr_parametri
    }

    return render(request, "info.html", context)

def baza(request):
    return render(request, 'baza.html')


def exemplu(request):
    return render(request, 'magazin_de_bijuterii/exemplu.html')



def test_accesare(request):
    ip_client = request.META.get('REMOTE_ADDR')
    url = request.build_absolute_uri()

    acc = Accesare(ip_client=ip_client, url=url)
    acc.save()

    rezultat = f"""
        <h2>Test clasa Accesare</h2>
        <p><b>ID:</b> {acc.id}</p>
        <p><b>IP client:</b> {acc.ip_client}</p>
        <p><b>URL complet:</b> {acc.url_complet()}</p>
        <p><b>Pagina:</b> {acc.pagina()}</p>
        <p><b>Data (default):</b> {acc.data()}</p>
        <p><b>Data formatată:</b> {acc.data('%d-%m-%Y %H:%M:%S')}</p>
        <p><b>Parametri URL:</b> {acc.lista_parametri()}</p>
    """
    return HttpResponse(rezultat)

numar_accesari_server = 0

def log(request):
    global numar_accesari_server
    numar_accesari_server += 1
    param_ultimele = request.GET.get("ultimele", None)
    param_accesari = request.GET.get("accesari", None)
    param_iduri = request.GET.getlist("iduri")
    param_dubluri = request.GET.get("dubluri", "false").lower() == "true"
    from magazin_de_bijuterii.models import Accesare
    Accesare.objects.create(
        ip_client=request.META.get('REMOTE_ADDR', '0.0.0.0'),
        url=request.get_full_path()
    )
    toate_accesarile = Accesare.objects.all().order_by("-id")
    context = {}

    if param_ultimele is not None:
        try:
            n = int(param_ultimele)
            total = toate_accesarile.count()
            if n > total:
                context["mesaj"] = f"Exista doar {total} accesari fata de {n} accesari cerute."
                accesari = toate_accesarile
            else:
                accesari = toate_accesarile[:n]

            context["accesari"] = accesari
        except ValueError:
            context["eroare"] = "Parametrul 'ultimele' trebuie să fie un număr întreg."
            context["accesari"] = []
    else:
        context["accesari"] = toate_accesarile

    if param_accesari == "nr":
        context["numar_accesari_server"] = numar_accesari_server
    elif param_accesari == "detalii":
        context["detalii_accesari"]=[a.data("%Y-%m-%d %H:%M:%S") for a in toate_accesarile]
    if param_iduri:
        toate_idurile = []
        for val in param_iduri:
            for i in val.split(","):
                if i.isdigit():
                    toate_idurile.append(int(i))

        if not param_dubluri:
            iduri_finale = []
            for i in toate_idurile:
                if i not in iduri_finale:
                    iduri_finale.append(i)
        else:
            iduri_finale = toate_idurile

        accesari_selectate = []
        for i in iduri_finale:
            acc = Accesare.objects.filter(id=i).first()
            if acc:
                accesari_selectate.append(acc)
        context["accesari"] = accesari_selectate

   
    param_tabel = request.GET.get("tabel", None)

    if param_tabel:
        if param_tabel == "tot":
            context["campuri"] = ["id", "ip_client", "url", "timestamp"]
            context["tabel_date"] = [
                {
                    "id": a.id,
                    "ip_client": a.ip_client,
                    "url": a.url,
                    "timestamp": a.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
                }
                for a in toate_accesarile
            ]
        else:
            campuri = [c.strip() for c in param_tabel.split(",") if c.strip()]
            context["campuri"] = campuri
            context["tabel_date"] = []
            for a in toate_accesarile:
                acc = {}
                if "id" in campuri:
                    acc["id"] = a.id
                if "ip_client" in campuri:
                    acc["ip_client"] = a.ip_client
                if "url" in campuri:
                    acc["url"] = a.url
                if "timestamp" in campuri:
                    acc["timestamp"] = a.timestamp.strftime("%d-%m-%Y %H:%M:%S")
                context["tabel_date"].append(acc)
    
    if toate_accesarile.exists():
        pagini = [urlparse(a.url).path or "/" for a in toate_accesarile]
        frecvente = Counter(pagini)
        pagina_max = max(frecvente, key=frecvente.get)
        pagina_min = min(frecvente, key=frecvente.get)
        context["pagina_max"] = pagina_max
        context["accesari_max"] = frecvente[pagina_max]
        context["pagina_min"] = pagina_min
        context["accesari_min"] = frecvente[pagina_min]
    else:
        context["pagina_max"] = None
        context["pagina_min"] = None
    return render(request, "magazin_de_bijuterii/log.html", context)


def index(request):
    user_ip = request.META.get('REMOTE_ADDR')  
    return render(request, 'magazin_de_bijuterii/index.html', {'user_ip': user_ip})


def despre(request):
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'despre.html', {'user_ip': user_ip})

def in_lucru(request):
    user_ip = request.META.get('REMOTE_ADDR')
    return render(request, 'in_lucru.html', {'user_ip': user_ip})


def produse(request):
    sort_order = request.GET.get('sort', 'a')
    produse_list = Produs.objects.select_related('categorie', 'brand').all()

    form = ProduseFilterForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data['nume']:
            produse_list = produse_list.filter(nume__icontains=form.cleaned_data['nume'])
        if form.cleaned_data['categorie']:
            produse_list = produse_list.filter(categorie=form.cleaned_data['categorie'])
        if form.cleaned_data['brand']:
            produse_list = produse_list.filter(brand=form.cleaned_data['brand'])
        if form.cleaned_data['pret_min']:
            produse_list = produse_list.filter(pret__gte=form.cleaned_data['pret_min'])
        if form.cleaned_data['pret_max']:
            produse_list = produse_list.filter(pret__lte=form.cleaned_data['pret_max'])

    if sort_order == 'd':
        produse_list = produse_list.order_by('-pret')
    else:
        produse_list = produse_list.order_by('pret')

    form = ProduseFilterForm(request.GET or None)

    if form.is_valid():
            produse_pe_pagina = form.cleaned_data.get('produse_pe_pagina') or 5
    else:
            produse_pe_pagina = 5


    paginator = Paginator(produse_list, produse_pe_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    mesaj_paginare = None
    if 'produse_pe_pagina' in request.GET:
        mesaj_paginare = (
            "⚠️ Ai schimbat numărul de produse pe pagină. "
            "Este posibil să fi sărit peste unele produse sau să le revezi pe cele deja vizualizate."
        )

    return render(request, 'magazin_de_bijuterii/produse.html', {
        'page_obj': page_obj,
        'titlu': 'Toate produsele',
        'sort_order': sort_order,
        'form': form,
        'mesaj_paginare': mesaj_paginare
    })


def produse_categorie(request, categorie_nume):
    categorie = get_object_or_404(Categorie, nume=categorie_nume)

    sort_order = request.GET.get('sort', 'a')
    produse_list = Produs.objects.select_related('categorie', 'brand').filter(categorie=categorie)

    form = ProduseFilterForm(request.GET or None)

    form.fields['categorie'].initial = categorie
    form.fields['categorie'].widget = forms.HiddenInput()

    if form.is_valid():
        data = form.cleaned_data
        if data.get('categorie') and data['categorie'] != categorie:
            from django.contrib import messages
            messages.error(request, "Categoria selectată nu poate fi modificată manual.")
            data['categorie'] = categorie

        if data['nume']:
            produse_list = produse_list.filter(nume__icontains=data['nume'])
        if data['brand']:
            produse_list = produse_list.filter(brand=data['brand'])
        if data['pret_min']:
            produse_list = produse_list.filter(pret__gte=data['pret_min'])
        if data['pret_max']:
            produse_list = produse_list.filter(pret__lte=data['pret_max'])
        produse_pe_pagina = data.get('produse_pe_pagina') or 5
    else:
        produse_pe_pagina = 5

    produse_list = produse_list.order_by('-pret' if sort_order == 'd' else 'pret')

    paginator = Paginator(produse_list, produse_pe_pagina)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    mesaj_paginare = None
    if 'produse_pe_pagina' in request.GET:
        mesaj_paginare = (
            "⚠️ Ai schimbat numărul de produse pe pagină. "
            "Este posibil să fi sărit peste unele produse sau să le revezi pe cele deja vizualizate."
        )

    return render(request, 'magazin_de_bijuterii/produse.html', {
        'page_obj': page_obj,
        'titlu': f"Produse: {categorie.nume}",
        'categorie': categorie,
        'sort_order': sort_order,
        'form': form,
        'mesaj_paginare': mesaj_paginare,
    })


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            data.pop("confirmare_email", None)  
            today = datetime.today()
            nastere = request.POST.get("data_nasterii")
            if nastere:
                try:
                    dn = datetime.strptime(nastere, "%Y-%m-%d")
                    ani = today.year - dn.year
                    luni = today.month - dn.month
                    if today.day < dn.day:
                        luni -= 1
                    if luni < 0:
                        luni += 12
                        ani -= 1
                    data["varsta"] = f"{ani} ani și {luni} luni"
                except Exception:
                    data["varsta"] = "necunoscut"

            mesaj = data.get("mesaj", "")
            mesaj = mesaj.replace("\n", " ")
            while "  " in mesaj:
                mesaj = mesaj.replace("  ", " ")
            import re
            def capitalize_after_punctuation(txt):
                return re.sub(r"(?<=[\.\?!])\s+([a-z])", lambda m: " " + m.group(1).upper(), txt)
            mesaj = capitalize_after_punctuation(mesaj)
            data["mesaj"] = mesaj.strip()

            tip = data.get("tip_mesaj", "").lower()
            zile = data.get("minim_zile_asteptare", 0)
            urgent = False
            if (tip in ["review", "cerere"] and zile == 4) or (tip in ["cerere", "intrebare"] and zile == 2):
                urgent = True
            data["urgent"] = urgent

            ip_address = request.META.get("REMOTE_ADDR", "necunoscut")
            timestamp = int(time.time())
            data["ip"] = ip_address
            data["timestamp"] = timestamp
            data["data_trimiterii"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            folder_path = os.path.join(os.path.dirname(__file__), "Mesaje")
            os.makedirs(folder_path, exist_ok=True)

            file_name = f"mesaj_{timestamp}"
            if urgent:
                file_name += "_urgent"
            file_name += ".json"

            file_path = os.path.join(folder_path, file_name)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            messages.success(request, f"Mesajul tău a fost trimis și salvat în {file_name}! 🚀")
            form = ContactForm()  
        else:
            messages.error(request, "Formularul conține erori. Te rugăm să verifici câmpurile.")
    else:
        form = ContactForm()

    return render(request, "magazin_de_bijuterii/contact.html", {"form": form})

def cos_virtual(request):
    return render(request, 'magazin_de_bijuterii/cos_virtual.html')

def despre(request):
    return render(request, 'magazin_de_bijuterii/despre.html')

def produs_detaliu(request, produs_id):
    produs = get_object_or_404(Produs, id=produs_id)
    return render(request, 'magazin_de_bijuterii/produs_detaliu.html', {'produs': produs})

def contact_view(request):
    mesaj_salvat = None
    eroare = None

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()
            data.pop('confirmare_email', None)

            ip_address = request.META.get('REMOTE_ADDR', 'necunoscut')
            timestamp = int(time.time())
            data['ip'] = ip_address
            data['timestamp'] = timestamp
            data['data_trimiterii'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            file_name = f"mesaj_{timestamp}"
            if data.get('urgent'):
                file_name += "_urgent"
            file_name += ".json"

            folder_path = os.path.join(os.path.dirname(__file__), 'Mesaje')
            os.makedirs(folder_path, exist_ok=True)

            file_path = os.path.join(folder_path, file_name)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            mesaj_salvat = f"Mesajul a fost salvat cu succes în {file_name} ✅"
            form = ContactForm()  
        else:
            eroare = "Formularul conține erori. Te rugăm să corectezi câmpurile evidențiate."
    else:
        form = ContactForm()

    return render(request, 'magazin_de_bijuterii/contact.html', {
        'form': form,
        'mesaj_salvat': mesaj_salvat,
        'eroare': eroare
    })
    
def adauga_produs(request):
    if request.method == "POST":
        form = ProdusForm(request.POST)
        if form.is_valid():
            produs = form.save(commit=False)
            produs.save()
            messages.success(request, "Produsul a fost adăugat cu succes! ✅")
            return redirect('produse')  #
        else:
            messages.error(request, "Formularul conține erori. Verifică câmpurile.")
    else:
        form = ProdusForm()

    return render(request, "magazin_de_bijuterii/adauga_produs.html", {"form": form})
def adauga_in_cos(request, produs_id):
    produs = get_object_or_404(Produs, id=produs_id)

    imagine_url = produs.imagini.first().url_imagine if produs.imagini.exists() else None

    produs_in_cos = {
        "id": produs.id,
        "nume": produs.nume,
        "pret": float(produs.pret),
        "imagine": imagine_url,
        "categorie": produs.categorie.nume,
        "brand": produs.brand.nume,
    }
    cos = request.session.get("cos", [])
    if not isinstance(cos, list):
        cos = [] 

    cos.append(produs_in_cos)
    request.session["cos"] = cos
    request.session.modified = True

    messages.success(request, f"✅ {produs.nume} a fost adăugat în coș!")
    return redirect("produse")

def sterge_din_cos(request, produs_id):
    cos = request.session.get('cos', {})
    if str(produs_id) in cos:
        del cos[str(produs_id)]
        request.session['cos'] = cos
        messages.info(request, "Produsul a fost șters din coș.")
    return redirect('vizualizare_cos')
def vizualizare_cos(request):
    cos = request.session.get('cos', [])
    total = sum(item['pret'] for item in cos)

    return render(request, 'magazin_de_bijuterii/cos_virtual.html', {
        'cos': cos,
        'total': total,
        'titlu': "Coșul meu 🛍️"
    })

def goleste_cos(request):
    request.session['cos'] = {}
    messages.info(request, "Coșul a fost golit.")
    return redirect('vizualizare_cos')
