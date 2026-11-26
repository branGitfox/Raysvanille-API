from time import time
from typing import List, Optional, Sequence, Tuple

from fastapi import UploadFile, BackgroundTasks
from pwdlib import PasswordHash
from app.config.config import settings
from fastapi import HTTPException, status
from email_free_fast_email import send_email as smtp_send_email
password_context = PasswordHash.recommended()
import os
import re
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


# ======================================================================
# EMAILS
# ======================================================================

import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from html import escape

BRAND = {
    "name": "Ray's Vanille",
    "site": "http://57.128.67.164/",
    "logo_url": "http://57.128.67.164/Logo_Ray_s_Vanille.avif",  # URL publique de ton logo (laisse vide pour afficher le nom en texte)
    "currency": "€",        # devise affichée dans le récapitulatif de commande
    "bg": "#F6EFE3",        # fond crème
    "card": "#FFFDF8",      # carte blanche cassée
    "text": "#3B2A1E",      # brun foncé
    "muted": "#8A7563",     # brun clair
    "accent": "#B8893B",    # doré vanille
    "danger": "#A94438",    # rouge brique (commande annulée)
    "dark": "#2B1D14",      # brun très foncé (header/footer)
}

# Identifiants SMTP : à mettre dans des variables d'environnement (ou dans settings)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "raysvanille@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


# ----------------------------------------------------------------------
# Modèles d'emails. Dans les textes, tu peux utiliser des variables :
# {first_name} {order_id} {total} {brand} ... (toute clé passée dans le contexte)
# Dans les messages, tu peux aussi mettre des liens : [texte du lien](https://...)
# ----------------------------------------------------------------------
EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "Bienvenue chez {brand}",
        "title": "Bienvenue chez {brand} !",
        "message": (
            "Merci d'avoir créé votre compte. Découvrez notre vanille de Madagascar, "
            "cultivée et préparée avec soin."
        ),
        "cta_label": "Découvrir la boutique",
        "preheader": "Votre compte est prêt, bienvenue !",
        "accent": "accent",
        "show_order": False,
    },
    "order_received": {
        "subject": "Nous avons bien reçu votre commande n° {order_id}",
        "title": "Commande reçue",
        "message": (
            "Nous avons bien reçu votre commande n° {order_id}. "
            "Nous la vérifions et vous écrirons dès qu'elle sera confirmée."
        ),
        "cta_label": "Voir ma commande",
        "preheader": "Commande n° {order_id} bien reçue",
        "accent": "accent",
        "show_order": True,
    },
    "order_confirmed": {
        "subject": "Votre commande n° {order_id} est confirmée",
        "title": "Commande confirmée",
        "message": (
            "Bonne nouvelle : votre commande n° {order_id} est confirmée et "
            "en cours de préparation."
        ),
        "cta_label": "Suivre ma commande",
        "preheader": "Commande n° {order_id} confirmée",
        "accent": "accent",
        "show_order": True,
    },
    "order_cancelled": {
        "subject": "Votre commande n° {order_id} a été annulée",
        "title": "Commande annulée",
        "message": (
            "Votre commande n° {order_id} a été annulée. "
            "Si vous avez des questions, n'hésitez pas à nous contacter."
        ),
        "cta_label": "Retourner à la boutique",
        "preheader": "Commande n° {order_id} annulée",
        "accent": "danger",
        "show_order": True,
    },
}


class _SafeDict(dict):
    """Laisse {variable} telle quelle si elle n'est pas fournie (pas d'erreur)."""
    def __missing__(self, key):
        return "{" + key + "}"


def _fmt(text: str, ctx: dict) -> str:
    return str(text).format_map(_SafeDict(ctx))


_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")


def render_text(text: str, accent: str) -> str:
    """Échappe le texte (sécurité), puis transforme [texte](url) en lien cliquable
    et les retours à la ligne en <br>."""
    safe = escape(text)
    safe = _LINK_RE.sub(
        lambda m: f'<a href="{m.group(2)}" style="color:{accent};text-decoration:underline;">{m.group(1)}</a>',
        safe,
    )
    return safe.replace("\n", "<br>")


def _money(value, currency: str) -> str:
    try:
        return f"{float(value):,.2f}".replace(",", " ") + f" {currency}"
    except (TypeError, ValueError):
        return f"{value} {currency}"


def _order_block(items: Sequence[dict], total, currency: str, accent: str) -> str:
    """Récapitulatif de commande. items = [{"name":..., "quantity":..., "price":...}]"""
    b = BRAND
    if not items and total is None:
        return ""
    rows = ""
    for it in items or []:
        qty = it.get("quantity", 1)
        rows += (
            f'<tr>'
            f'<td style="padding:8px 0;border-bottom:1px solid #EADFCB;font-size:14px;color:{b["text"]};">{escape(str(it.get("item_name", "")))}</td>'
            f'<td align="center" style="padding:8px 0;border-bottom:1px solid #EADFCB;font-size:14px;color:{b["muted"]};">x{escape(str(qty))}</td>'
            f'<td align="right" style="padding:8px 0;border-bottom:1px solid #EADFCB;font-size:14px;color:{b["text"]};">{escape(_money(it.get("price", 0), currency))}</td>'
            f'</tr>'
        )
    total_row = ""
    if total is not None:
        total_row = (
            f'<tr>'
            f'<td colspan="2" style="padding:12px 0 0;font-size:15px;font-weight:bold;color:{b["text"]};">Total</td>'
            f'<td align="right" style="padding:12px 0 0;font-size:15px;font-weight:bold;color:{accent};">{escape(_money(total, currency))}</td>'
            f'</tr>'
        )
    return f"""
        <tr>
          <td style="padding:8px 40px 0;font-family:Arial,Helvetica,sans-serif;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
              {rows}
              {total_row}
            </table>
          </td>
        </tr>"""


def build_html(kind: str, ctx: dict) -> str:
    """Construit le HTML de l'email pour un type donné (welcome, order_received, ...)."""
    b = BRAND
    tpl = EMAIL_TEMPLATES[kind]
    accent = b[tpl["accent"]]

    ctx = {"brand": b["name"], **ctx}
    first_name = escape(str(ctx.get("first_name", "")))
    title = escape(_fmt(ctx.get("title") or tpl["title"], ctx))
    message_raw = _fmt(ctx.get("message") or tpl["message"], ctx)
    preheader = _fmt(ctx.get("preheader") or tpl["preheader"], ctx)
    cta_label = _fmt(ctx.get("cta_label") or tpl["cta_label"], ctx)
    cta_url = escape(ctx.get("cta_url") or b["site"], quote=True)
    currency = ctx.get("currency", b["currency"])

    message_html = render_text(message_raw, accent)

    # Motif (utile pour une annulation)
    reason_html = ""
    if ctx.get("reason"):
        reason_html = (
            f'<p style="margin:16px 0 0;font-family:Arial,Helvetica,sans-serif;font-size:14px;'
            f'line-height:1.6;color:{b["muted"]};">Motif : {render_text(str(ctx["reason"]), accent)}</p>'
        )

    # Récapitulatif de commande
    order_html = ""
    if tpl["show_order"]:
        order_html = _order_block(ctx.get("items") or [], ctx.get("total"), currency, accent)

    # Liens supplémentaires [(label, url), ...]
    extra_links_html = ""
    extra_links: Sequence[Tuple[str, str]] = ctx.get("links") or []
    if extra_links:
        parts = " &nbsp;•&nbsp; ".join(
            f'<a href="{escape(url, quote=True)}" style="color:{accent};text-decoration:none;">{escape(label)}</a>'
            for label, url in extra_links
        )
        extra_links_html = (
            f'<tr><td align="center" style="padding:0 40px 24px;font-family:Arial,Helvetica,sans-serif;'
            f'font-size:13px;">{parts}</td></tr>'
        )

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

        <!-- Bande de couleur -->
        <tr><td style="height:4px;background:{accent};font-size:0;line-height:0;">&nbsp;</td></tr>

        <!-- Contenu -->
        <tr>
          <td style="padding:40px 40px 16px;font-family:Georgia,'Times New Roman',serif;color:{b['text']};">
            <h1 style="margin:0 0 16px;font-size:28px;font-weight:normal;color:{b['text']};">
              Bonjour {first_name},
            </h1>
            <h2 style="margin:0 0 16px;font-size:18px;font-weight:normal;color:{accent};">
              {title}
            </h2>
            <p style="margin:0;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.7;color:{b['text']};">
              {message_html}
            </p>
            {reason_html}
          </td>
        </tr>

        <!-- Récapitulatif commande (si applicable) -->
        {order_html}

        <!-- Bouton -->
        <tr>
          <td align="center" style="padding:24px 40px 24px;">
            <a href="{cta_url}"
               style="display:inline-block;background:{accent};color:#ffffff;text-decoration:none;
                      font-family:Arial,Helvetica,sans-serif;font-size:15px;font-weight:bold;
                      letter-spacing:1px;padding:14px 36px;border-radius:999px;">
              {escape(cta_label)}
            </a>
          </td>
        </tr>

        <!-- Liens supplémentaires -->
        {extra_links_html}

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


def _build_plain_text(kind: str, ctx: dict) -> str:
    """Version texte brut (fallback des clients mail sans HTML)."""
    tpl = EMAIL_TEMPLATES[kind]
    ctx = {"brand": BRAND["name"], **ctx}
    # [texte](url) -> texte : url
    message = _LINK_RE.sub(r"\1 : \2", _fmt(ctx.get("message") or tpl["message"], ctx))
    lines = [f"Bonjour {ctx.get('first_name', '')},", "", message]

    if ctx.get("reason"):
        lines += ["", f"Motif : {ctx['reason']}"]

    if tpl["show_order"] and ctx.get("items"):
        currency = ctx.get("currency", BRAND["currency"])
        lines += [""]
        for it in ctx["items"]:
            lines.append(f"- {it.get('name', '')} x{it.get('quantity', 1)} : {_money(it.get('price', 0), currency)}")
        if ctx.get("total") is not None:
            lines.append(f"Total : {_money(ctx['total'], currency)}")

    cta_label = _fmt(ctx.get("cta_label") or tpl["cta_label"], ctx)
    lines += ["", f"{cta_label} : {ctx.get('cta_url') or BRAND['site']}"]

    for label, url in ctx.get("links") or []:
        lines.append(f"{label} : {url}")

    lines += ["", BRAND["name"]]
    return "\n".join(lines)


def send_mail(kind: str, to_email: str, first_name: str, **context) -> bool:
    """
    Envoie un email dynamique.

    kind : "welcome" | "order_received" | "order_confirmed" | "order_cancelled"
    context (tous optionnels) :
        order_id, items=[{"name","quantity","price"}], total, currency,
        message, title, subject, preheader, cta_label, cta_url,
        reason (motif d'annulation), links=[("Label", "https://...")]
    """
    if kind not in EMAIL_TEMPLATES:
        raise ValueError(f"Type d'email inconnu : {kind}")

    ctx = {"first_name": first_name, "brand": BRAND["name"], **context}
    subject = _fmt(ctx.get("subject") or EMAIL_TEMPLATES[kind]["subject"], ctx)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((BRAND["name"], SMTP_USER))
    msg["To"] = to_email
    msg.set_content(_build_plain_text(kind, ctx))
    msg.add_alternative(build_html(kind, ctx), subtype="html")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(msg)

        print("Email envoyé avec succès !")
        return True

    except smtplib.SMTPAuthenticationError:
        print("Erreur : authentification Gmail échouée.")
    except Exception as e:
        print(f"Erreur d'envoi : {e}")
    return False


# Raccourcis pratiques
def send_welcome_email(to_email: str, first_name: str, **ctx):
    return send_mail("welcome", to_email, first_name, **ctx)


def send_order_received_email(to_email: str, first_name: str, order_id, items=None, total=None, **ctx):
    return send_mail("order_received", to_email, first_name, order_id=order_id, items=items, total=total, **ctx)


def send_order_confirmed_email(to_email: str, first_name: str, order_id, items=None, total=None, **ctx):
    return send_mail("order_confirmed", to_email, first_name, order_id=order_id, items=items, total=total, **ctx)


def send_order_cancelled_email(to_email: str, first_name: str, order_id, items=None, total=None, reason=None, **ctx):
    return send_mail("order_cancelled", to_email, first_name, order_id=order_id, items=items, total=total, reason=reason, **ctx)


# Ancienne fonction conservée (même signature) : email libre avec le design de marque
def send_test_email(cta: str, title: str, first_name: str, preheader: str, to_email: str, message:str):
    return send_mail(
        "welcome",
        to_email,
        first_name,
        subject="Bienvenue chez Ray's Vanille",
        title=title,
        message=message,
        cta_label=cta,
        preheader=preheader,
    )


# envoie queue de mail
async def send_queued_mail(kind: str, to_email: str, first_name: str, queue: BackgroundTasks, **context):
    queue.add_task(send_mail, kind, to_email, first_name, **context)
    return {"status": "email delivré"}