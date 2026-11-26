from time import time
from typing import List

from fastapi import UploadFile, BackgroundTasks
from pwdlib import PasswordHash
from app.config.config import settings
from fastapi import HTTPException, status
from email_free_fast_email import send_email as smtp_send_email
password_context = PasswordHash.recommended()
import os
import shutil

def hash_password(plaintext:str):
    return password_context.hash(plaintext)


def verify_password(plaintext:str, hashed):
    return password_context.verify(plaintext, hashed)


# pour gérer les uploads d'images dynamiquement
def upload_pictures(public_path:str, image:UploadFile|None, allow_file_extension:List[str])->str:
    os.makedirs(public_path, exist_ok=True)
    try:
        if image:

            file = image.file
            filename = image.filename
            image_ext = str(filename).split('.')[-1]
            if image_ext not in allow_file_extension:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Fichier non pris en charge (ex: jpeg, png, jpg)")
            new_filename = str(time()) + "." + image_ext
            filepath = os.path.join(public_path, new_filename)
            with open(filepath, "wb") as f:
                shutil.copyfileobj(file, f)
            return f"{settings.api_url}/" + filepath
        else:
            return os.path.join(f"{settings.api_url}/" + public_path, "/default.png")

    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="impossible d'importer l'image")



# Gérer l'auto suppression d'une image ancien lors de modification d'un article
def remove_old_pictures(image:UploadFile, old_image:str):
    if image is not None:
        if os.path.exists(old_image[len(f"{settings.api_url}/"):]):
            os.remove(old_image[len(f"{settings.api_url}/"):])


# Gérer l'auto suppression d'une image
def remove_pictures(image:str):
    if os.path.exists(image[len(f"{settings.api_url}/"):]):
            os.remove(image[len(f"{settings.api_url}/"):])


# pour l'envoie d'email


import smtplib
from email.message import EmailMessage


import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from html import escape

BRAND = {
    "name": "Ray's Vanille",
    "site": "http://57.128.67.164/",
    "logo_url": "http://57.128.67.164/Logo_Ray_s_Vanille.avif",  # URL publique de ton logo (laisse vide pour afficher le nom en texte)
    "bg": "#F6EFE3",        # fond crème
    "card": "#FFFDF8",      # carte blanche cassée
    "text": "#3B2A1E",      # brun foncé
    "muted": "#8A7563",     # brun clair
    "accent": "#B8893B",    # doré vanille
    "dark": "#2B1D14",      # brun très foncé (header/footer)
}


def build_html(first_name, title, message, cta_label, cta_url, preheader=""):
    b = BRAND
    first_name, title, message = escape(first_name), escape(title), escape(message)
    logo = (
        f'<img src="{b["logo_url"]}" alt="{b["name"]}" height="48" style="display:block;margin:0 auto;border:0;">'
        if b["logo_url"]
        else f'<span style="font-family:Georgia,\'Times New Roman\',serif;font-size:28px;'
             f'letter-spacing:2px;color:{b["accent"]};">{b["name"].upper()}</span>'
    )

    return f"""\
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:{b['bg']};">
  <!-- Preheader (texte d'aperçu dans la boîte de réception) -->
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;color:{b['bg']};">{escape(preheader)}</div>

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{b['bg']};">
    <tr><td align="center" style="padding:32px 12px;">

      <table role="presentation" width="600" cellpadding="0" cellspacing="0"
             style="width:100%;max-width:600px;background:{b['card']};border-radius:16px;overflow:hidden;
                    box-shadow:0 4px 20px rgba(59,42,30,0.08);">

        <!-- Header -->
        <tr>
          <td align="center" style="background:{b['dark']};padding:32px 24px;">
            {logo}
            <div style="font-family:Arial,Helvetica,sans-serif;font-size:12px;letter-spacing:3px;
                        color:#CBB89A;margin-top:8px;text-transform:uppercase;">
              Vanille de Madagascar
            </div>
          </td>
        </tr>

        <!-- Bande dorée -->
        <tr><td style="height:4px;background:{b['accent']};font-size:0;line-height:0;">&nbsp;</td></tr>

        <!-- Contenu -->
        <tr>
          <td style="padding:40px 40px 16px;font-family:Georgia,'Times New Roman',serif;color:{b['text']};">
            <h1 style="margin:0 0 16px;font-size:28px;font-weight:normal;color:{b['text']};">
              Bonjour {first_name},
            </h1>
            <h2 style="margin:0 0 16px;font-size:18px;font-weight:normal;color:{b['accent']};">
              {title}
            </h2>
            <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.7;color:{b['text']};">
              {message}
            </p>
          </td>
        </tr>

        <!-- Bouton -->
        <tr>
          <td align="center" style="padding:24px 40px 40px;">
            <a href="{cta_url}"
               style="display:inline-block;background:{b['accent']};color:#ffffff;text-decoration:none;
                      font-family:Arial,Helvetica,sans-serif;font-size:15px;font-weight:bold;
                      letter-spacing:1px;padding:14px 36px;border-radius:999px;">
              {escape(cta_label)}
            </a>
          </td>
        </tr>

        <!-- Séparateur -->
        <tr><td style="padding:0 40px;"><hr style="border:0;border-top:1px solid #EADFCB;margin:0;"></td></tr>

        <!-- Footer -->
        <tr>
          <td align="center" style="padding:24px 40px 32px;font-family:Arial,Helvetica,sans-serif;
                                    font-size:12px;line-height:1.6;color:{b['muted']};">
            Vous recevez cet email car vous êtes en relation avec {b['name']}.<br>
            <a href="{b['site']}" style="color:{b['accent']};text-decoration:none;">{b['site'].replace('https://', '')}</a><br>
            © 2026 {b['name']}. Tous droits réservés.
          </td>
        </tr>
      </table>

    </td></tr>
  </table>
</body>
</html>
"""



import smtplib

from email.message import EmailMessage
from email.utils import formataddr


async def send_test_email(to_email: str, message:str):
    email_user = "raysvanille@gmail.com"
    email_password = "jpyk otxt vvst rzdc"

    to_email = to_email

    server = "smtp.gmail.com"
    port = 587

    subject = "Bienvenue chez Ray's Vanille"
    first_name = "Client"

    message = message

    cta_url = BRAND["site"]

    html = build_html(
        first_name,
        "Le parfum de la vraie vanille",
        message,
        "Découvrir nos produits",
        cta_url,
        preheader="Découvrez notre sélection de vanille."
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((BRAND["name"], email_user))
    msg["To"] = to_email

    msg.set_content(
        f"Bonjour {first_name},\n\n"
        f"{message}\n\n"
        f"Découvrir : {cta_url}\n\n"
        f"{BRAND['name']}"
    )

    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(server, port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(email_user, email_password)
            smtp.send_message(msg)

        print("Email envoyé avec succès !")

    except smtplib.SMTPAuthenticationError:
        print("Erreur : authentification Gmail échouée.")

    except Exception as e:
        print(f"Erreur d'envoi : {e}")



# envoie queue de mail
async def send_queued_mail(to_email:str, message:str, queue: BackgroundTasks):
    queue.add_task(send_test_email, to_email, message)
    return {"status": "email delivré"}
