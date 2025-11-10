from django import forms
from django.core.exceptions import ValidationError 
from .models import Categorie, Brand, Produs
from datetime import date, datetime
import re

class ProduseFilterForm(forms.Form):
    nume = forms.CharField(
        label='Nume produs',
        required=False,
        max_length=100
    )
    categorie = forms.ModelChoiceField(
        queryset=Categorie.objects.all(),
        label='Categorie',
        required=False,
        empty_label='Toate categoriile'
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        label='Brand',
        required=False,
        empty_label='Toate brandurile'
    )
    pret_min = forms.DecimalField(
        label='Preț minim',
        required=False,
        min_value=0
    )
    pret_max = forms.DecimalField(
        label='Preț maxim',
        required=False,
        min_value=0
    )
    produse_pe_pagina = forms.IntegerField(
    label='Produse pe pagină',
    min_value=1,
    max_value=50,
    required=False,
    initial=5
    )

    def clean(self):
        cleaned_data = super().clean()
        pret_min = cleaned_data.get("pret_min")
        pret_max = cleaned_data.get("pret_max")

        if pret_min and pret_max and pret_min > pret_max:
            raise ValidationError("Prețul minim nu poate fi mai mare decât prețul maxim.")
        return cleaned_data

    def clean_nume(self):
        nume = self.cleaned_data.get("nume")
        if nume and not all(ch.isalpha() or ch.isspace() for ch in nume):
            raise ValidationError("Numele produsului trebuie să conțină doar litere.")
        return nume
    

def validate_capitalized_text(value):
    """Textul trebuie să înceapă cu majusculă și să conțină doar litere, spațiu și cratimă."""
    if not re.match(r'^[A-Z][a-zA-Z\s\-]*$', value):
        raise ValidationError("Textul trebuie să înceapă cu majusculă și să conțină doar litere, spații sau cratimă.")


def validate_capital_after_space_or_dash(value):
    """Verifică dacă după spațiu sau cratimă urmează o literă mare."""
    if re.search(r'[\s\-][a-z]', value):
        raise ValidationError("După spațiu sau cratimă trebuie să urmeze o literă mare.")


def validate_email_domain(value):
    """Interzice e-mailuri temporare."""
    if any(domain in value for domain in ["guerillamail.com", "yopmail.com"]):
        raise ValidationError("E-mailurile temporare (guerillamail, yopmail) nu sunt permise.")


def validate_message_length_and_links(value):
    """Mesaj între 5-100 cuvinte, niciun cuvânt >15 caractere, fără linkuri."""
    words = re.findall(r'\b\w+\b', value)
    if len(words) < 5 or len(words) > 100:
        raise ValidationError("Mesajul trebuie să conțină între 5 și 100 de cuvinte.")
    for w in words:
        if len(w) > 15:
            raise ValidationError("Niciun cuvânt nu trebuie să depășească 15 caractere.")
    if re.search(r'\bhttps?://\S+', value):
        raise ValidationError("Mesajul nu poate conține linkuri (http/https).")


def validate_subject_no_links(value):
    """Subiectul nu trebuie să conțină linkuri."""
    if re.search(r'\bhttps?://\S+', value):
        raise ValidationError("Subiectul nu poate conține linkuri.")


def validate_cnp(value):
    """CNP doar cifre, începe cu 1/2, și are o dată validă în următoarele 6 cifre."""
    if not value.isdigit():
        raise ValidationError("CNP-ul trebuie să conțină doar cifre.")
    if value[0] not in ('1', '2'):
        raise ValidationError("CNP-ul trebuie să înceapă cu 1 (bărbat) sau 2 (femeie).")
    try:
        an = int(value[1:3])
        luna = int(value[3:5])
        zi = int(value[5:7])
        an += 1900  
        datetime(an, luna, zi)
    except ValueError:
        raise ValidationError("CNP-ul conține o dată invalidă (ZZ/LL/AA).")



class ContactForm(forms.Form):
    TIP_MESAJ_CHOICES = [
        ('neselectat', 'Neselectat'),
        ('reclamatie', 'Reclamație'),
        ('intrebare', 'Întrebare'),
        ('review', 'Review'),
        ('cerere', 'Cerere'),
        ('programare', 'Programare'),
    ]

    nume = forms.CharField(label="Nume", max_length=10, required=True)
    prenume = forms.CharField(label="Prenume", max_length=10, required=False)
    cnp = forms.CharField(label="CNP", max_length=13, min_length=13, required=False)
    data_nasterii = forms.DateField(
        label="Data nașterii", widget=forms.DateInput(attrs={'type': 'date'}), required=True
    )
    email = forms.EmailField(label="E-mail", required=True)
    confirmare_email = forms.EmailField(label="Confirmare E-mail", required=True)
    tip_mesaj = forms.ChoiceField(
        label="Tip mesaj", choices=TIP_MESAJ_CHOICES, required=True, initial='neselectat'
    )
    subiect = forms.CharField(label="Subiect", max_length=100, required=True)
    minim_zile_asteptare = forms.IntegerField(
        label=(
            "Minim zile așteptare "
            "(Pentru review-uri/cereri minimul e 4 zile, "
            "iar pentru cereri/întrebări minim 2 zile. Maxim 30.)"
        ),
        min_value=1,
        max_value=30,
        required=True
    )
    mesaj = forms.CharField(
        label="Mesaj (te rugăm să te semnezi la final)",
        widget=forms.Textarea,
        required=True
    )

    # -------------------------
    # VALIDĂRI INDIVIDUALE
    # -------------------------
    def clean_cnp(self):
        cnp = self.cleaned_data.get('cnp')
        if cnp:
            if not cnp.isdigit():
                raise ValidationError("CNP-ul trebuie să conțină doar cifre.")
            if len(cnp) != 13:
                raise ValidationError("CNP-ul trebuie să conțină exact 13 cifre.")
            if cnp[0] not in ('1', '2', '5', '6'):
                raise ValidationError("CNP-ul trebuie să înceapă cu 1/2 (1900–1999) sau 5/6 (2000–2099).")

            try:
                an = int(cnp[1:3])
                luna = int(cnp[3:5])
                zi = int(cnp[5:7])

                # Determinăm secolul în funcție de prima cifră
                if cnp[0] in ('1', '2'):
                    an += 1900
                elif cnp[0] in ('5', '6'):
                    an += 2000

                # Verificăm dacă data este validă
                datetime(an, luna, zi)

            except ValueError:
                raise ValidationError("CNP-ul conține o dată invalidă (ZZ/LL/AA).")

        return cnp

    # -------------------------
    # VALIDĂRI ȘI PREPROCESĂRI GLOBALE
    # -------------------------
    def clean(self):
        cleaned_data = super().clean()

        nume = cleaned_data.get("nume")
        mesaj = cleaned_data.get("mesaj")
        email = cleaned_data.get("email")
        confirmare_email = cleaned_data.get("confirmare_email")
        tip_mesaj = cleaned_data.get("tip_mesaj")
        zile = cleaned_data.get("minim_zile_asteptare")
        data_nasterii = cleaned_data.get("data_nasterii")
        cnp = cleaned_data.get("cnp")

        # -------------------
        # VALIDĂRI GLOBALE
        # -------------------

        # 1️⃣ Emailurile trebuie să coincidă
        if email and confirmare_email and email != confirmare_email:
            raise ValidationError("❌ Adresele de e-mail nu coincid.")

        # 2️⃣ Verificare semnătură în mesaj (ultimul cuvânt = numele)
        if mesaj and nume:
            cuvinte_mesaj = mesaj.strip().split()
            if not cuvinte_mesaj or cuvinte_mesaj[-1].lower() != nume.lower():
                raise ValidationError("✍️ Mesajul trebuie să se încheie cu numele tău ca semnătură.")

        # 3️⃣ Zile de așteptare în funcție de tipul mesajului
        if tip_mesaj and zile:
            if tip_mesaj in ['review', 'cerere'] and zile < 4:
                raise ValidationError("⏳ Pentru review-uri și cereri este necesar un minim de 4 zile.")
            elif tip_mesaj in ['cerere', 'intrebare'] and zile < 2:
                raise ValidationError("⏳ Pentru cereri și întrebări este necesar un minim de 2 zile.")
            elif zile > 30:
                raise ValidationError("⚠️ Numărul maxim de zile permis este 30.")

        # 4️⃣ CNP ↔ Data nașterii
        if cnp and data_nasterii:
            try:
                prefix = cnp[0]
                an = int(cnp[1:3])
                if prefix in ('1', '2'):
                    an += 1900
                elif prefix in ('5', '6'):
                    an += 2000
                luna_cnp = int(cnp[3:5])
                zi_cnp = int(cnp[5:7])
                data_din_cnp = date(an, luna_cnp, zi_cnp)
                if data_din_cnp != data_nasterii:
                    raise ValidationError("🧾 Data nașterii nu corespunde cu cea din CNP.")
            except Exception:
                raise ValidationError("❗ CNP-ul are un format invalid pentru verificarea cu data nașterii.")

        # -------------------
        # PREPROCESĂRI
        # -------------------

        # 1️⃣ Înlocuiește data_nasterii cu vârsta exprimată în ani și luni
        if data_nasterii:
            azi = date.today()
            ani = azi.year - data_nasterii.year
            luni = azi.month - data_nasterii.month
            if azi.day < data_nasterii.day:
                luni -= 1
            if luni < 0:
                ani -= 1
                luni += 12
            cleaned_data["varsta"] = f"{ani} ani și {luni} luni"
            cleaned_data["data_nasterii"] = cleaned_data["varsta"]

        # 2️⃣ Normalizează mesajul:
        #    - linii noi → spații
        #    - spații multiple → un singur spațiu
        #    - literă mare după ., ?, !, ...
        if mesaj:
            text = mesaj.replace('\n', ' ')
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'(?<=[\.\?!…])\s*([a-z])', lambda m: ' ' + m.group(1).upper(), text)
            cleaned_data["mesaj"] = text.strip()

        # 3️⃣ Setează urgent = True dacă zile == minimul cerut
        urgent = False
        if tip_mesaj and zile:
            if (tip_mesaj in ['review', 'cerere'] and zile == 4) or \
               (tip_mesaj in ['cerere', 'intrebare'] and zile == 2):
                urgent = True
        cleaned_data["urgent"] = urgent

        return cleaned_data
def validate_starts_with_capital(value):
    if not value[0].isupper():
        raise ValidationError("Numele trebuie să înceapă cu o literă mare.")

def validate_no_special_chars(value):
    if not re.match(r'^[A-Za-z0-9\s\-]+$', value):
        raise ValidationError("Numele nu trebuie să conțină caractere speciale (doar litere, cifre și cratimă).")

def validate_description_min_words(value):
    words = value.split()
    if len(words) < 3:
        raise ValidationError("Descrierea trebuie să conțină cel puțin 3 cuvinte.")

# --- FORMULARUL PRINCIPAL ---

class ProdusForm(forms.ModelForm):
    confirmare_pret = forms.DecimalField(
        label="Confirmare preț (lei)",
        required=True,
        min_value=0,
        help_text="Introduceți din nou prețul pentru confirmare."
    )

    class Meta:
        model = Produs
        fields = ['nume', 'descriere', 'pret', 'brand', 'categorie']
        labels = {
            'nume': 'Nume produs',
            'descriere': 'Descriere detaliată',
            'pret': 'Preț (lei)',
            'brand': 'Brand asociat',
            'categorie': 'Categorie produs'
        }
        help_texts = {
            'nume': 'Trebuie să înceapă cu literă mare și să nu conțină simboluri speciale.',
            'descriere': 'Scrie o descriere clară și coerentă (minim 3 cuvinte).'
        }
        # Un câmp cu două validări externe
        validators = {
            'nume': [validate_starts_with_capital, validate_no_special_chars]
        }

    # --- VALIDĂRI PE CÂMPURI ---

    def clean_pret(self):
        pret = self.cleaned_data.get('pret')
        if pret is not None and pret <= 0:
            raise forms.ValidationError("Prețul trebuie să fie mai mare decât 0 lei.")
        return pret

    def clean_descriere(self):
        descriere = self.cleaned_data.get('descriere', '')
        validate_description_min_words(descriere)
        if len(descriere) > 300:
            raise ValidationError("Descrierea este prea lungă (maxim 300 de caractere).")
        return descriere

    # --- VALIDARE MULTI-CÂMP ---

    def clean(self):
        cleaned_data = super().clean()
        pret = cleaned_data.get('pret')
        confirmare_pret = cleaned_data.get('confirmare_pret')
        categorie = cleaned_data.get('categorie')

        if pret and confirmare_pret and pret != confirmare_pret:
            raise ValidationError("Prețul introdus și confirmarea nu coincid.")

        if categorie and categorie.nume.lower() == "lux" and pret and pret < 500:
            raise ValidationError("Produsele din categoria 'Lux' trebuie să aibă un preț de cel puțin 500 lei.")

        return cleaned_data

    # --- SALVARE CU commit=False ---

    def save(self, commit=True):
        produs = super().save(commit=False)
        produs.data_adaugare = datetime.now()
        produs.cod = f"PRD-{int(datetime.timestamp(datetime.now()))}"
        if commit:
            produs.save()
        return produs