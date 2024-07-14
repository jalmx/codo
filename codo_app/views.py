import threading
import uuid
from os import path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect

from codo_app.util.helper_views import (
    add_data_teacher,
    add_path_uri,
    create_bulk_commissions,
    create_teacher_ghost,
    delete_commission,
    load_teachers_from_csv,
)
from codo_app.util.log import *
from . import models
from .util.read_pdf import ReadDataPDF
from .util.send_email import send_bulk_email

# Create your views here.


def index(request):
    create_teacher_ghost()

    if request.method == "GET" and request.GET.get("delete"):
        id = request.GET.get("delete")
        delete_commission(id)

    context = {"title": "CODO"}
    commissions = models.Commissions.objects.all()
    context["commissions"] = commissions
    return render(request=request, template_name="index.html", context=context)


def home_teacher(request, data=None):
    context = {"title": "Registro Docente"}

    if request.POST.get("edit"):
        email = request.POST.get("edit")
        teacher = models.Teachers.objects.get(email1=email)
        context["teacher"] = teacher

    teachers = models.Teachers.objects.all().exclude(name="UNKNOWN")

    context["teachers"] = teachers
    return render(request=request,
                  template_name="teacher.html",
                  context=context)


def register_teacher(request):
    context = {"title": "Registro Docente"}

    if request.method == "POST":
        try:
            id = request.POST.get("id") or None
            name_teacher = request.POST["name_teacher"].upper()
            email_main = request.POST["email_main"].lower()
            email_second = request.POST["email_second"].lower() or None
            print("----------------")
            print(request.POST)
            print("----------------")
            if id:
                old_teacher = models.Teachers.objects.get(id_teacher=id)
                print("-----------------")
                print(old_teacher)
                print("-----------------")
                old_teacher.name = name_teacher
                old_teacher.email1 = email_main
                old_teacher.email2 = email_second
                old_teacher.save()
                print(f"Updating: {old_teacher}")
            else:
                models.Teachers.objects.create(
                    name=name_teacher,
                    email1=email_main,
                    email2=email_second if email_second else "",
                )
                print(
                    f"Insertar {name_teacher} , {email_main}, {email_second}")

            return redirect("/docentes", context=context)
        except Exception as e:
            print(f"Error al insertar: {e}")
            l(__name__, f"Error al insertar docente", type=E, error=e)

            return redirect("/docentes",
                            error="register",
                            context=context,
                            status_code=503)

    return redirect("/docentes")


def delete_teacher(request):
    email = request.POST.get("delete")
    try:
        teacher = models.Teachers.objects.get(email1=email)
        teacher.delete()
        return redirect("/docentes/")
    except:
        return redirect("/docentes/", error="error_delete")


def load_teachers(request):
    if request.method == "POST":
        csv_file = request.FILES["file_csv"]

        content = csv_file.read().decode("utf-8")

        rows = content.split("\n")
        ok = load_teachers_from_csv(rows)
        if not ok:
            return redirect("/docentes/#fail")

    return redirect("/docentes/")


def send_bulk(request):

    def update(commissions, status):
        """Callback to update each email sended

        Args:
            commissions (integer): id from commission
            status (bool): status from email
        """
        commissions.status = status
        commissions.save()

    if request.method == "POST":

        id_commission = request.POST.get("id_commission")

        # print(request.POST.get("message_to_email"))
        # print(request.POST.get("message_to_email_json"))

        print(f"El id es: {id_commission}")
        l(__name__, f"Comenzando a enviar la comisión id: {id_commission}")
        if id_commission:
            commission_main = models.Commissions.objects.all().get(
                id_commissions=id_commission)
            commission_main.text_html = request.POST.get(
                "message_to_email") or ""
            commission_main.text_json = request.POST.get(
                "message_to_email_json") or ""
            # print("====> comision main: ", commission_main)
            commission_main.status = "p"
            commission_main.save()

            commissions_to_send = models.Commission.objects.all().filter(
                id_commissions=id_commission)
            threading.Thread(
                target=send_bulk_email,
                name=f"Sending emails id commission: {id_commission}",
                args=(
                    commissions_to_send,
                    commission_main.text_html,
                    update,
                ),
            ).start()

    return redirect("/")


def create_commission(request):
    if request.method == "GET" and request.GET.get("commission"):
        id = request.GET.get("commission")
        commissions_main = models.Commissions.objects.all().get(
            id_commissions=id)
        commissions = models.Commission.objects.all().filter(
            id_commissions=commissions_main.id_commissions)

        teachers = []
        context = {
            "title": "Comisión",
            "name": commissions_main.name,
            "foliate": commissions_main.foliate_commission,
            "file_path_base": commissions_main.pdf_master.name,
            "id_commissions": commissions_main.id_commissions,
            "status": commissions_main.status,
        }

        print(f"el contexto: {context}")
        for commission in commissions:
            teachers.append({
                "status":
                commission.status,
                "foliate":
                commission.foliate_teacher,
                "uri":
                commission.uri,
                "name":
                (commission.id_teacher.name
                 if not (commission.id_teacher.name == "UNKNOWN") else
                 ReadDataPDF(commission.path_pdf).get_data()[0]["name"]),
                "email1":
                (commission.id_teacher.email1 if commission.id_teacher.email1
                 != "email@email.com" else "SIN CORREO"),
                "email2":
                (commission.id_teacher.email2
                 if commission.id_teacher.email2 != "email@email.com" else ""),
                "exist": (True if commission.id_teacher.email1
                          != "email@email.com" else False),
            })

        context["teachers"] = teachers

        return render(request=request,
                      template_name="commissions.html",
                      context=context)

    if request.method == "POST":
        name_commission = request.POST["name-commission"]
        foliate_commission = request.POST["foliate"]

        pdf = request.FILES["add_pdf"]

        fs = FileSystemStorage()

        name_new_pdf = f"{pdf.name.replace('.pdf', '')}_{uuid.uuid4()}.pdf"
        pdf_name = fs.save(name_new_pdf, pdf)

        url = fs.url(pdf_name)

        context = {
            "title": "Creando Comisión",
            "name": name_commission,
            "foliate": foliate_commission,
            "file_path_base": url,
        }

        commission = models.Commissions.objects.create(
            name=name_commission,
            foliate_commission=foliate_commission,
            pdf_master=url,
            date=str(datetime.datetime.now()),
        )

        path_pdf_saved = path.join(settings.MEDIA_ROOT, name_new_pdf)

        content_pdf = ReadDataPDF(path_pdf_saved)
        content_pdf.get_data()

        path_files = path.join(settings.MEDIA_ROOT, name_new_pdf)

        data_files = content_pdf.split(
            path_pdf_saved,
            path.join(settings.MEDIA_ROOT, path_files.replace(".pdf", "")),
        )

        l(__name__, "Comisión id created: ", commission.id_commissions)

        data_files = add_path_uri(data_files)
        data_files = add_data_teacher(data_files, commission)

        creation_ok = create_bulk_commissions(data_files)

        context["teachers"] = data_files
        context["id_commissions"] = commission.id_commissions
        context["status"] = "c" if creation_ok else "f"

        if not creation_ok:
            delete_commission(commission.id_commissions)

        return render(request=request,
                      template_name="commissions.html",
                      context=context)

    return redirect("/")


def register_email(request):
    """Function to save, delete and get emails from host

    Args:
        request (Request): _description_

    Returns:
        _type_: template html with context from db emails
    """
    ctx = {}
    if request.method == "POST":
        if request.POST.get("email") and request.POST.get("password"):
            email = request.POST.get("email")
            pwd = request.POST.get("password")
            models.EmailBase.objects.create(email=email.strip(),
                                            password=pwd.strip())
        elif request.POST.get("id"):
            id = request.POST.get("id")
            print("el id a eliminar", id)
            models.EmailBase.objects.all().get(id=int(id)).delete()

    emails = models.EmailBase.objects.all()
    ctx["emails"] = emails

    return render(request=request,
                  template_name="register_email.html",
                  context=ctx)
