from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render

from codo_app.util.helper_views import (
    add_data_teacher,
    add_path_uri,
    create_bulk_commissions,
    create_teacher_ghost,
)
from . import models
from django.core.files.storage import FileSystemStorage
import uuid
from datetime import datetime
from django.conf import settings
from os import path
from .util.read_pdf import ReadDataPDF
from django.views.decorators.csrf import csrf_exempt
from .util.send_email import send_bulk_email
import threading

# Create your views here.


def index(request):
    create_teacher_ghost()

    if request.method == "GET" and request.GET.get("delete"):
        id = request.GET.get("delete")
        try:
            commission = models.Commissions.objects.get(id_commissions=id)
            # TODO: Eliminar la carpeta y el pdf
            commission.delete()
        except:
            print("El id de la comisión no existe")

    context = {"title": "CODO"}
    commissions = models.Commissions.objects.all()
    context["commissions"] = commissions
    return render(request=request, template_name="index.html", context=context)


def home_teacher(request, data=None):
    context = {"title": "Registro Docente"}

    if data:
        # print(f"data que viene: {data}")
        if data == "error":
            context["error"] = "register"

    if request.POST.get("edit"):
        email = request.POST.get("edit")
        teacher = models.Teachers.objects.get(email1=email)
        context["teacher"] = teacher
    elif request.POST.get("update"):
        # TODO: agregar la secuencia de actualización del docente
        pass

    teachers = models.Teachers.objects.all()

    context["teachers"] = teachers
    return render(request=request, template_name="teacher.html", context=context)


def register_teacher(request):

    context = {"title": "Registro Docente"}
    try:
        name_teacher = request.POST["name_teacher"].upper()
        email_main = request.POST["email_main"].upper()
        email_second = request.POST["email_second"].upper() or None

        models.Teachers.objects.create(
            name=name_teacher, email1=email_main, email2=email_second
        )

        return redirect("/docentes", context=context)
    except Exception as e:
        print(f"Error al insertar: {e}")

        return redirect("/docentes", error="register", context=context, status_code=503)


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
        teachers = []
        for i, row in enumerate(rows[1:]):
            columns = row.strip().split(",")

            if len(columns) > 1:
                name = columns[0].upper().strip()
                email1 = columns[1].lower().strip()
                email2 = columns[2].lower().strip() or None

                teachers.append(
                    models.Teachers(name=name, email1=email1, email2=email2)
                )
        try:
            if len(teachers) > 0:
                models.Teachers.objects.bulk_create(teachers)
        except:
            pass
    return redirect("/docentes/")


def send_bulk(request):

    def update(commissions, status):
        commissions.status = status
        commissions.save()

    if request.method == "POST":

        id_commission = request.POST.get("id_commission")

        if id_commission:
            commissions_to_send = models.Commission.objects.all().filter(
                id_commissions=id_commission
            )
            threading.Thread(
                target=send_bulk_email,
                name=f"Sending emails id commission: {id_commission}",
                args=(
                    commissions_to_send,
                    update,
                ),
            ).start()
            # send_bulk_email(commissions_to_send, update)

    return redirect("/")


def create_commission(request):

    if request.method == "GET" and request.GET.get("commission"):
        id = request.GET.get("commission")
        commissions_main = models.Commissions.objects.all().get(id_commissions=id)
        commissions = models.Commission.objects.all().filter(
            id_commissions=commissions_main.id_commissions
        )
        teachers = []
        context = {
            "title": "Comisión",
            "name": commissions_main.name,
            "foliate": commissions_main.foliate_commission,
            "file_path_base": commissions_main.pdf_master.name,
            "id_commissions": commissions_main.id_commissions,
            "status": commissions_main.status,
        }
        for commission in commissions:
            if commission.id_teacher.name != "UNKNOWN":
                teachers.append(
                    {
                        "status": commission.status,
                        "foliate_teacher": commission.foliate_teacher,
                        "uri": commission.uri,
                        "name": commission.id_teacher.name,
                        "email1": (
                            commission.id_teacher.email1
                            if commission.id_teacher.email1 != "email@email.com"
                            else ""
                        ),
                        "email2": (
                            commission.id_teacher.email2
                            if commission.id_teacher.email2 != "email@email.com"
                            else ""
                        ),
                        "exist": (
                            True
                            if commission.id_teacher.email1 != "email@email.com"
                            else False
                        ),
                    }
                )

        context["teachers"] = teachers

        return render(
            request=request, template_name="commissions.html", context=context
        )

    if request.method == "POST":

        name_commission = request.POST["name-commission"]
        foliate_commission = request.POST["foliate"]

        pdf = request.FILES["add_pdf"]

        fs = FileSystemStorage()

        name_new_pdf = f"{pdf.name.replace('.pdf','')}_{uuid.uuid4()}.pdf"
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
            date=str(datetime.now()),
        )

        path_pdf_saved = path.join(settings.MEDIA_ROOT, name_new_pdf)

        content_pdf = ReadDataPDF(path_pdf_saved)
        content_pdf.get_data()

        path_files = path.join(settings.MEDIA_ROOT, name_new_pdf)

        data_files = content_pdf.split(
            path_pdf_saved,
            path.join(settings.MEDIA_ROOT, path_files.replace(".pdf", "")),
        )

        # print("Comision id: ", commission.id_commissions)

        data_files = add_path_uri(data_files)
        data_files = add_data_teacher(data_files, commission)

        create_bulk_commissions(data_files)

        context["teachers"] = data_files
        context["id_commissions"] = commission.id_commissions
        context["status"] = "C"

        # print("=" * 80)
        # print(data_files)
        # print("=" * 80)

        return render(
            request=request, template_name="commissions.html", context=context
        )

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
            models.EmailBase.objects.create(email=email.strip(), password=pwd.strip())
        elif request.POST.get("id"):
            id = request.POST.get("id")
            print("el id a eliminar", id)
            models.EmailBase.objects.all().get(id=int(id)).delete()
            
    emails = models.EmailBase.objects.all()
    ctx["emails"] = emails

    return render(request=request, template_name="register_email.html", context=ctx)
