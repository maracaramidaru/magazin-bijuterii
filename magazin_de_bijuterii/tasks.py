import logging
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger("django")


def sterge_useri_neconfirmati():
    limita = timezone.now() - timedelta(
    minutes=settings.DELETE_UNCONFIRMED_USERS_EVERY_K_MINUTES
 )
    useri = User.objects.filter(
        is_active=False,
        date_joined__lt=limita
    )

    for u in useri:
        logger.warning(f"Utilizator șters (email neconfirmat): {u.username}")
        u.delete()

def trimite_newsletter():
    limita = timezone.now() - timedelta(
        minutes=settings.NEWSLETTER_MIN_USER_AGE
    )

    useri = User.objects.filter(
        date_joined__lt=limita,
        is_active=True,
        email__isnull=False
    ).exclude(email="")

    mesaje = [
        "Descoperă noile bijuterii din colecția noastră ✨",
        "Promoții exclusive pentru membrii noștri!",
        "Cele mai vândute bijuterii ale săptămânii 💎",
        "Reduceri speciale la bijuterii elegante!"
    ]

    for u in useri:
        continut = random.choice(mesaje)

        send_mail(
            subject="Newsletter Magazin Bijuterii",
            message=continut,
            from_email="noreply@bijuterii.ro",
            recipient_list=[u.email],
            fail_silently=True,
        )

        logger.info(f"Newsletter trimis către {u.email}: {continut}")


def statistica_produse():
    logger.debug("Task periodic: statistica produse executat")


def curata_loguri():
    logger.info("Task zilnic: curățare logică loguri executat")
