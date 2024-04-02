from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("docentes/", views.home_teacher, name="docentes"),
    path("docentes/<data>", views.home_teacher, name="docentes"),
    path("registerTeacher", views.register_teacher),
    path("delete", views.delete_teacher),
    path("comision", views.create_commission),
    path("load_teachers", views.load_teachers),
    path("send_bulk", views.send_bulk),
    path("emails", views.register_email),
]
