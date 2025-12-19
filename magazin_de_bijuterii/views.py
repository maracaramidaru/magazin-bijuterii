from django.shortcuts import render,get_object_or_404, redirect
from .models import Produs, Categorie, Brand, Material, Dimensiune, Imagine,Vizualizare,Promotie,N
from datetime import datetime
from urllib.parse import urlparse
from django.http import HttpResponse
from .models import Accesare
from .models import CustomUser
from collections import Counter
from urllib.parse import urlparse
from django.core.paginator import Paginator
from .forms import ProduseFilterForm, ContactForm, ProdusForm,PromotieForm

from django.contrib import messages
from django import forms
import os
import json
import time
from .forms import InregistrareForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login
import secrets
from django.contrib.auth import login, logout, get_user_model, update_session_auth_hash
from django.core.mail import send_mail, mail_admins
from django.utils import timezone
from datetime import timedelta
import random
import string
import logging
from django.core.mail import send_mass_mail
from django.db.models import Count, Q




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
    messages.info(request, "Ai accesat pagina Info.")    #mesaj-info
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
    
    
    
    from magazin_de_bijuterii.models import Accesare
    
    if not request.user.is_authenticated or not request.user.groups.filter(name="Administratori_site").exists():
        # incrementăm accesările 403
        numar_accesari = request.session.get("numar_accesari_403", 0) + 1
        request.session["numar_accesari_403"] = numar_accesari

        salut = f"Salut {request.user.username}" if request.user.is_authenticated else "Salut preastimate anonim"

        context = {
            "salut": salut,
            "titlu": "Eroare acces log",
            "mesaj_personalizat": "Nu ai voie să accesezi pagina /log",
            "numar_accesari": numar_accesari,
            "limita_accesari": settings.N_MAX_403,
        }

        return render(request, "magazin_de_bijuterii/403.html", context, status=403)
    global numar_accesari_server
    numar_accesari_server += 1
    param_ultimele = request.GET.get("ultimele", None)
    param_accesari = request.GET.get("accesari", None)
    param_iduri = request.GET.getlist("iduri")
    param_dubluri = request.GET.get("dubluri", "false").lower() == "true"
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
    messages.info(request, "Ai accesat pagina de loguri.")  #mesaj-info
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
    if not request.user.has_perm("magazin_de_bijuterii.add_produs"):
        # creștem numărul accesărilor pentru pagina 403
        numar_accesari = request.session.get("numar_accesari_403", 0) + 1
        request.session["numar_accesari_403"] = numar_accesari
        messages.debug(request, "A intrat în view-ul de adăugare produs.")  #mesaj-debug
        salut = f"Salut {request.user.username}" if request.user.is_authenticated else "Salut preastimate anonim"

        context = {
            "salut": salut,
            "titlu": "Eroare adaugare produse",
            "mesaj_personalizat": "Nu ai voie să adaugi produse",
            "numar_accesari": numar_accesari,
            "limita_accesari": settings.N_MAX_403,
        }

        return render(request, "magazin_de_bijuterii/403.html", context, status=403)
    

    
    if request.method == "POST":
        form = ProdusForm(request.POST)
        if form.is_valid():
            produs = form.save(commit=False)
            produs.save()
            messages.success(request, "Produsul a fost adăugat cu succes! ✅")
            return redirect('produse')
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







logger = logging.getLogger('django')  # logging ASK4

User = get_user_model()


def trimite_email(subiect, mesaj_text, mesaj_html):
    try:
        mail_admins(
            subject=subiect,
            message=mesaj_text,
            html_message=mesaj_html
        )
        logger.info(f"Email trimis administratorilor: {subiect}")  # INFO
    except Exception as e:
        logger.error(f"Eroare la trimiterea email-ului: {str(e)}")  # ERROR

def verifica_logare_suspecta(request, username):
    now = timezone.now()
    
    # încărcăm ce e în sesiune și convertim în datetime
    failed_attempts_raw = request.session.get('failed_logins', [])
    failed_attempts = []
    
    for t_str in failed_attempts_raw:
        try:
            t = datetime.fromisoformat(t_str)
            if now - t < timedelta(minutes=2):
                failed_attempts.append(t_str)  
        except:
            pass
    failed_attempts.append(now.isoformat())
    request.session['failed_logins'] = failed_attempts
    if len(failed_attempts) >= 3:
        ip = request.META.get('REMOTE_ADDR', 'N/A')
        subiect = "Logari suspecte"
        mesaj_text = f"Username: {username}\nIP: {ip}"
        mesaj_html = f"<h1 style='color:red'>{subiect}</h1><p>{mesaj_text.replace(chr(10), '<br>')}</p>"
        trimite_email(subiect, mesaj_text, mesaj_html)
        logger.warning(f"Logari suspecte detectate: {username} de la IP {ip}")  # WARNING


def genereaza_cod():
    cod = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    logger.debug(f"Cod unic generat: {cod}")  # DEBUG
    return cod


def inregistrare_view(request):
    try:
        if request.method == "POST":
            form = InregistrareForm(request.POST)

            if form.is_valid():
                username = form.cleaned_data['username'].lower()
                if username == 'admin':
                    subiect = "Cineva incearca sa ne preia site-ul"
                    email_utilizator = form.cleaned_data.get('email', 'N/A')
                    mesaj_text = f"Email folosit: {email_utilizator}"
                    mesaj_html = f"<h1 style='color:red'>{subiect}</h1><p>{mesaj_text}</p>"
                    trimite_email(subiect, mesaj_text, mesaj_html)
                    logger.warning(f"Încercare de înregistrare cu username interzis: {username}")  # WARNING
                    form.add_error('username', 'Acest username nu este permis.')
                    return render(request, "magazin_de_bijuterii/inregistrare.html", {"form": form})

                user = form.save(commit=False)
                user.cod = genereaza_cod()
                user.email_confirmat = False
                user.save()
                logger.info(f"Utilizator înregistrat: {user.username}")  # INFO

                link_confirmare = f"http://127.0.0.1:8000/confirma_mail/{user.cod}/"
                subiect_email = "Bine ai venit la Magazinul nostru!"
                message_html = render_to_string('magazin_de_bijuterii/email_confirmare.html', {
                    'user': user,
                    'link_confirmare': link_confirmare
                })
                mesaj_text = f"Salut {user.username}, confirmă emailul aici: {link_confirmare}"

                try:
                    send_mail(
                        subiect_email,
                        mesaj_text,
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        html_message=message_html
                    )
                    logger.info(f"Email confirmare trimis către {user.email}")  # INFO
                except Exception as e:
                    logger.error(f"Eroare la trimiterea email-ului către {user.email}: {str(e)}")  # ERROR
                    mesaj_html_err = f"<div style='background:red; color:white; padding:10px;'>Eroare trimitere email: {str(e)}</div>"
                    trimite_email("Eroare email", str(e), mesaj_html_err)

                return render(request, "magazin_de_bijuterii/confirmare_email.html", {
                    "user": user,
                    "link_confirmare": link_confirmare
                })
            else:
                logger.warning(f"Formular inregistrare invalid: {form.errors}")  # WARNING
        else:
            form = InregistrareForm()
            logger.debug("Pagina de inregistrare accesata")  # DEBUG

        return render(request, "magazin_de_bijuterii/inregistrare.html", {"form": form})
    except Exception as e:
        logger.critical(f"Eroare fatală la procesarea înregistrării: {str(e)}")  # CRITICAL
        subiect = "Eroare fatală la procesarea înregistrării utilizatorului"
        mesaj_text = str(e)
        mesaj_html = f"<div style='background:red'><h1>{subiect}</h1><p>{mesaj_text}</p></div>"
        trimite_email(subiect, mesaj_text, mesaj_html)
        messages.error(request, "A apărut o eroare, administratorii au fost notificați.")
        return render(request, "magazin_de_bijuterii/inregistrare.html", {"form": InregistrareForm()})


def confirma_mail_view(request, cod):
    try:
        user = User.objects.get(cod=cod)
        user.email_confirmat = True
        user.cod = None
        user.save()
        messages.success(request, "Email confirmat cu succes! Te poți loga acum.") #succes-mesaj
        logger.info(f"Email confirmat pentru {user.username}")  # INFO
    except User.DoesNotExist:
        messages.error(request, "Cod invalid sau deja folosit.") #eroare-mesaj
        logger.warning(f"Cod invalid la confirmarea email-ului: {cod}")  # WARNING
    return redirect('login')


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if not form.is_valid():
            username = request.POST.get('username', 'N/A')
            verifica_logare_suspecta(request, username)
            logger.warning(f"Login eșuat pentru {username}")  # WARNING
        if form.is_valid():
            user = form.get_user()
            if not user.email_confirmat:
                form.add_error(None, "Trebuie să confirmi adresa de email înainte de logare.")
                logger.info(f"User {user.username} a incercat sa se logheze fara confirmare email")  # INFO
                return render(request, "magazin_de_bijuterii/login.html", {"form": form})

            login(request, user)
            messages.success(request, "Te-ai autentificat cu succes.") #succes-mesaj

            logger.info(f"Utilizator logat: {user.username}")  # INFO

            if form.cleaned_data.get("remember_me"):
                request.session.set_expiry(86400)
            else:
                request.session.set_expiry(0)

            request.session["user_data"] = {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "telefon": getattr(user, "telefon", ""),
                "tara": getattr(user, "tara", ""),
                "judet": getattr(user, "judet", ""),
                "oras": getattr(user, "oras", ""),
                "cod_postal": getattr(user, "cod_postal", ""),
            }

            return redirect("profil")
    else:
        form = LoginForm()
        logger.debug("Pagina de login accesata")  # DEBUG

    return render(request, "magazin_de_bijuterii/login.html", {"form": form})


def logout_view(request):
    logout(request)
    request.session.flush()
    logger.info("User deconectat")  # INFO
    return redirect("login")


@login_required
def profil_view(request):
    user_data = request.session.get("user_data")
    if not user_data:
        u = request.user
        user_data = {
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "telefon": getattr(u, "telefon", ""),
            "tara": getattr(u, "tara", ""),
            "judet": getattr(u, "judet", ""),
            "oras": getattr(u, "oras", ""),
            "cod_postal": getattr(u, "cod_postal", ""),
        }
        request.session["user_data"] = user_data
    logger.debug(f"Profil accesat pentru {request.user.username}")  # DEBUG
    return render(request, "magazin_de_bijuterii/profil.html", {"user_data": user_data})


def interzis_view(request):
    numar_accesari = request.session.get('numar_accesari_403', 0)
    numar_accesari += 1
    request.session['numar_accesari_403'] = numar_accesari

    if request.user.is_authenticated:
        salut = f"Salut {request.user.username}"
    else:
        salut = "Salut preastimate anonim"

    mesaj_personalizat = "Nu aveți permisiunea de a accesa această resursă."
    titlu = "Eroare adăugare produse"
    messages.debug(request, f"Număr accesări 403: {numar_accesari}") #mesaj-debug
    logger.warning(f"Acces interzis pagina 403, numar accesari: {numar_accesari}")  # WARNING

    context = {
        "salut": salut,
        "titlu": titlu,
        "mesaj_personalizat": mesaj_personalizat,
        "numar_accesari": numar_accesari,
        "limita_accesari": settings.N_MAX_403,
    }

    return render(request, "magazin_de_bijuterii/403.html", context, status=403)




N = 5  

def salveaza_vizualizare(utilizator, produs):
    # Salvăm vizualizarea
    vizualizare = Vizualizare.objects.create(user=utilizator, produs=produs, data_vizualizare=timezone.now())

    vizualizari_utilizator = Vizualizare.objects.filter(user=utilizator).order_by('-data_vizualizare')
    if vizualizari_utilizator.count() > N:
        
        for v in vizualizari_utilizator[N:]:
            v.delete()
            

def detalii_produs_view(request, produs_id):
    produs = get_object_or_404(Produs, id=produs_id)

    if request.user.is_authenticated:
        salveaza_vizualizare(request.user, produs)

    return render(request, "magazin_de_bijuterii/produs_detaliu.html", {"produs": produs})


K = 3 

@login_required
def promotii_view(request):
    if request.method == "POST":
        form = PromotieForm(request.POST)
        if form.is_valid():
            promotie = form.save(commit=False)
            promotie.data_creare = timezone.now()
            promotie.save()
            form.save_m2m()  # pentru ManyToMany cu categorii

            # Transformăm categoriile selectate într-o listă de obiecte Categorie
            categorii_selectate = form.cleaned_data['categorii']

            lista_mailuri = []

            for categorie in categorii_selectate:
                users = CustomUser.objects.annotate(
                    nr_viz=Count(
                        'vizualizare',
                        filter=Q(vizualizare__produs__categorie=categorie)
                    )
                ).filter(nr_viz__gte=K)

                if not users.exists():
                    continue
                template_path = os.path.join(
                    settings.BASE_DIR,
                    'magazin_de_bijuterii',
                    'templates',
                    'email_templates',
                    f'promo_{categorie.nume.lower()}.txt'
                )
                if not os.path.exists(template_path):
                    template_path = os.path.join(
                        settings.BASE_DIR,
                        'magazin_de_bijuterii',
                        'templates',
                        'email_templates',
                        'promo_template1.txt'
                    )

                with open(template_path, 'r', encoding='utf-8') as f:
                    mesaj_template = f.read()

                # Construim mesajul pentru fiecare utilizator
                for user in users:
                    mesaj_final = mesaj_template.format(
                        subiect=promotie.subiect,
                        data_expirare=promotie.data_expirare,
                        reducere_procent=promotie.reducere_procent,
                        cod_cupon=promotie.cod_cupon,
                        username=user.username,
                        nume_promotie=promotie.nume,
                        categorie_nume=categorie.nume
                    )
                    lista_mailuri.append((
                        promotie.subiect,
                        mesaj_final,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email]
                    ))

            if lista_mailuri:
                send_mass_mail(tuple(lista_mailuri), fail_silently=False)

            return HttpResponse("Promoția a fost trimisă!")
    else:
        form = PromotieForm()

    return render(request, "email_templates/promotii.html", {"form": form})



logger = logging.getLogger('django')

def test_logging(request):
    logger.debug("Mesaj DEBUG - test")
    logger.info("Mesaj INFO - test")
    logger.warning("Mesaj WARNING - test")
    logger.error("Mesaj ERROR - test")
    logger.critical("Mesaj CRITICAL - test")

    return HttpResponse("Am trimis toate nivelurile de log.")





#ex de adaugat in grup in manage.py shell:from django.contrib.auth.models import User, Group
# from django.contrib.auth.models import User, Group

# user = User.objects.get(username="MARAC1")
# grup = Group.objects.get(name="moderatori")

# user.groups.add(grup)
# user.save()


