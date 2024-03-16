from django.core.mail import send_mail, send_mass_mail, EmailMessage
from django.template.loader import render_to_string
from time import sleep
from ..models import Teachers, Commission, Commissions

EMAIL_BOT_LIST = [{
    "email1": "docentes.1@cbtis085.edu.mx",
    "pwd": "kBu>757RC*0v>X",
    "reply_to": "jalmx89@gmail.com"
}]


def _build_body(data: dict):

    html = render_to_string("correo.html", {"teacher": data})

    # print(html)
    return html


def send_email_one(one_data: dict):

    email = EmailMessage(
        one_data["subject"],
        one_data["body"],
        one_data["from_email"],
        one_data["to_emails"],  # is a list emails
        reply_to=one_data["reply_to"],
        fail_silently=False)

    email.attach_file(one_data["path_pdf"])
    return email


def _get_data_teacher(teacher: Teachers):

    return {
        "name": teacher.name,
        "email1": teacher.email1,
        "email2": teacher.email2 or None
    }


def _get_data_commissions(commission: Commissions):

    return {
        "name commission": commission.name,
        "date": commission.date,
        "status": commission.status
    }


def _get_data_commission(commission: Commission):
    return {
        "foliate_teacher": commission.foliate_teacher,
        "path_pdf": commission.path_pdf
    }


def send_bulk_email(data: list[Commission], cb_update):
    # print("----------------------")
    # print(data.values())
    print("----------------------")

    print(data.first().id_commission)

    for one in data:
        # print("----------------------")
        # print("Tipo de one", type(one))
        # print(one)
        # print("----------------------")
        info = {}
        info.update(_get_data_commission(one))
        info.update(_get_data_teacher(one.id_teacher))
        info.update(_get_data_commissions(one.id_commissions))

        print("---------------------")
        print("info", info)
        print("---------------------")

        try:
            emails = [info["email1"]]
            if info["email2"]:
                emails.append(info["email2"])

            send_email_one({
                "subject":
                f'Comisión: {info["name commission"]} - {info["date"]}',
                "body": _build_body(info),
                "from_email": [EMAIL_BOT_LIST[0]["email1"]],
                "to_emails": emails,
                "reply_to": [EMAIL_BOT_LIST[0]["reply_to"]]
            })

            one["status"] = "s"
            one.save()
            sleep(1)
            break
        except Exception as e:
            cb_update(data[0].id_commissions, "F")
            print(f"Fail to send email: {one}\n--->Error:{e}")
    cb_update(data[0].id_commissions, "D")
