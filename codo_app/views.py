from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render
from . import models

# Create your views here.


def index(request):
    context = {"title": "CODO"}
    commissions = models.Commissions.objects.all()
    context["commissions"] = commissions
    return render(request=request, template_name="index.html", context=context)


def home_teacher(request, data=None):
    context = {"title": "Registro Docente"}

    if data:
        print(f"data que viene: {data}")
        if data == "error":
            context["error"] = "register"

    if request.POST.get("edit"):
        email = request.POST.get("edit")
        teacher = models.Teachers.objects.get(email1=email)
        context["teacher"] = teacher
    elif request.POST.get("update"):
        # TODO: agregar la secuencia de actualizacion del docente
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
