from time import sleep

from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string

from codo_app.util.load_email import get_emails, get_reply_to
from codo_app.util.log import E, W, l
from ..models import Teachers, Commission, Commissions


def _build_body(data: dict):
    html = render_to_string("correo.html", {"teacher": data})

    print(f"el cuerpo del mensaje es: {html}")
    return html


def send_email_one(one_data: dict, connection=None):
    """Send one mail

    Args:
        one_data (dict): _description_
        connection (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    l(__name__, "enviar el correo a: ", get_emails())

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


def send_bulk_email(data: list[Commission], message_html: str, cb_update):
    """Send all emails

    Args:
        data (list[Commission]): _description_
        message_html (str): New message to add in email send
        cb_update (function): function callback to set state
    """
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
        info.update({"message": message_html})

        if info["email1"] == "email@email.com":
            l(__name__,
              f"No sended to {info} | because no have a email valid",
              type=W)
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

                print(f"el objeto para el correo: {info}")
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
