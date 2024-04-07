from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from time import sleep
from codo_app.util.log import *
from codo_app.util.load_email import get_emails, get_reply_to
from ..models import Teachers, Commission, Commissions


def _build_body(data: dict):

    html = render_to_string("correo.html", {"teacher": data})

    # print(html)
    return html


def send_email_one(one_data: dict, connection=None):
    print("enviar el correo a: ", get_emails())

    email = EmailMultiAlternatives(
        subject=f'Comisión: {one_data["name commission"]} - {one_data["date"]}',
        from_email=get_emails()[0]["email"],
        to=one_data["emails"],  # is a list emails
        reply_to=get_reply_to(),
        connection=connection,
    )

    email.attach_alternative(_build_body(one_data), "text/html")

    email.attach_file(one_data["path_pdf"])
    return email


def _get_data_teacher(teacher: Teachers):

    emails = [teacher.email1]

    emails.append(teacher.email2) if teacher.email2 else ""

    return {
        "name": teacher.name,
        "email1": teacher.email1,
        "email2": teacher.email2 or None,
        "emails": emails,
    }


def _get_data_commissions(commission: Commissions):

    return {
        "name commission": commission.name,
        "date": commission.date,
        "status": commission.status,
    }


def _get_data_commission(commission: Commission):
    return {
        "foliate_teacher": commission.foliate_teacher,
        "path_pdf": commission.path_pdf,
    }


def send_bulk_email(data: list[Commission], cb_update):
    # print("----------------------")
    # print(data.values())
    # print("----------------------")

    print("El id de la comisión main: ", data.first().id_commissions)
    l(__name__, "El id de la comisión main: ", data.first().id_commissions)

    for one in data:
        # print("----------------------")
        # print("Tipo de one", type(one))
        # print(one)
        # print("----------------------")
        
        info = {}
        info.update(_get_data_commission(one))
        info.update(_get_data_teacher(one.id_teacher))
        info.update(_get_data_commissions(one.id_commissions))
        
        if info["email1"] == "email@email.com":
            l(__name__, f"No sended to {info} | because no have a email valid", type=W)
            cb_update(data.first().id_commissions, "F")
            continue
        # print("---------------------")
        # print("info", info)
        # print("---------------------")

        try:
            with get_connection(
                password=get_emails()[0]["pwd"],
                username=get_emails()[0]["email"],
                fail_silently=False,
            ) as connection:
                send_email_one(info, connection).send(fail_silently=False)

                print(f'Enviando el correo a {info.get("email1")}')
                l(__name__, f'Enviando el correo a {info.get("email1")}')
                one.status = "s"
                one.save()

                sleep(1)

        except Exception as e:
            cb_update(data.first().id_commissions, "F")
            print(f"Fail to send email: {info}\n--->Error:{e}")
            l(__name__, f"Fail to send email: {info}\n--->Error:{e}", type=E)

    cb_update(data.first().id_commissions, "D")
