from django.core.mail import send_mail, send_mass_mail, EmailMessage
from django.template.loader import render_to_string
from time import sleep


def _build_body(data: dict):
    data = {"name": "Leyva", "foliate": "220(DOC)/324"}

    html = render_to_string("correo.html", {})

    print(html)
    return html


def send_email_one(one_data: dict):

    email = EmailMessage(
        one_data["subject"],
        one_data["body"],
        one_data["from_email"],
        one_data["to_emails"],  # is a list emails
        reply_to=["serviciosdocentes@cbtis085.com"],
        fail_silently=True)

    email.attach_file(one_data["path_pdf"])
    return email


def send_bulk_email(data: dict):

    for one in data:
        # aqui tengo que sacar la informacion y pasarlo al dict
        send_email_one(one).send(fail_silently=False)
        sleep(1)
