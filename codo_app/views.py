from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render
from . import models
from django.core.files.storage import FileSystemStorage
import uuid
from datetime import datetime
from django.conf import settings
from os import path
from .util.read_pdf import ReadDataPDF
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def create_teacher_ghost():
    """Function to create a register for elements no register in database
    """

    try:
        models.Teachers.objects.create(name="UNKNOWN",
                                       email1="email@email.com",
                                       email2="email@email.com")
    except:
        pass


def index(request):
    create_teacher_ghost()
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
    return render(request=request,
                  template_name="teacher.html",
                  context=context)


def register_teacher(request):

    context = {"title": "Registro Docente"}
    try:
        name_teacher = request.POST["name_teacher"].upper()
        email_main = request.POST["email_main"].upper()
        email_second = request.POST["email_second"].upper() or None

        models.Teachers.objects.create(name=name_teacher,
                                       email1=email_main,
                                       email2=email_second)

        return redirect("/docentes", context=context)
    except Exception as e:
        print(f"Error al insertar: {e}")

        return redirect("/docentes",
                        error="register",
                        context=context,
                        status_code=503)


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
                    models.Teachers(name=name, email1=email1, email2=email2))
        try:
            if len(teachers) > 0:
                models.Teachers.objects.bulk_create(teachers)
        except:
            pass
    return redirect("/docentes/")


def add_path_uri(data_dict: list):

    for data in data_dict:
        data["uri"] = data.get("path_file").replace(str(settings.MEDIA_ROOT),
                                                    "/file")

    return data_dict


def add_data(data_dict: list, commission_main):

    for teacher in data_dict:
        try:
            teacher_model = models.Teachers.objects.get(name=teacher["name"])
            teacher["id_teacher"] = teacher_model
            teacher["email1"] = teacher_model.email1
            teacher["email2"] = teacher_model.email2 or None
            teacher["exist"] = True
        except:
            teacher["id_teacher"] = models.Teachers.objects.get(name="UNKNOWN")
            teacher["exist"] = False
        finally:
            teacher["status"] = "p"
            teacher["id_commission"] = commission_main

    return data_dict


def create_bulk_commissions(data_commission_list: list):

    for commission in data_commission_list:
        create_register_commission_one(commission)

    return True


def create_register_commission_one(data_commission: dict):
    # print(f"comssion a registrar: {data_commission}")
    commission = models.Commission.objects.create(
        status=data_commission["status"],
        foliate_teacher=data_commission["foliate"],
        uri=data_commission["uri"],
        path_pdf=data_commission["path_file"],
        id_commissions=data_commission["id_commission"],
        id_teacher=data_commission["id_teacher"])

    return commission

def send_emails(data):

    for commission in data:
        pass


@csrf_exempt
def send_bulk(request):

    if request.method == "POST":

        id_commission = request.POST.get("id_commission")

        if id_commission:
            commissions_to_send = models.Commission.objects.all().filter(
                id_commissions=id_commission)
            send_emails(commissions_to_send)

    return redirect("/")


def create_commission(request):

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
        data_files = add_data(data_files, commission)

        create_bulk_commissions(data_files)

        context["teachers"] = data_files
        context["id_commissions"] = commission.id_commissions

        # print("=" * 80)
        # print(data_files)
        # print("=" * 80)

        return render(request=request,
                      template_name="commissions.html",
                      context=context)

    return redirect("/")
