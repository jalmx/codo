from os import path

from django.conf import settings

from codo.settings import BASE_DIR
from codo_app import models
from codo_app.util.log import *
from codo_app.util.util import delete_files


def add_path_uri(data_dict: list):
    for data in data_dict:
        data["uri"] = data.get("path_file").replace(str(settings.MEDIA_ROOT), "/file")

    return data_dict


def add_data_teacher(data_dict: list, commission_main):
    for teacher in data_dict:
        try:
            teacher_model = models.Teachers.objects.get(name=teacher["name"])
            teacher["id_teacher"] = teacher_model
            teacher["email1"] = teacher_model.email1
            teacher["email2"] = teacher_model.email2 or None
            teacher["status"] = "p"
            teacher["exist"] = True
        except:
            teacher["id_teacher"] = models.Teachers.objects.get(name="UNKNOWN")
            teacher["exist"] = False
            teacher["status"] = "f"
        finally:
            teacher["id_commission"] = commission_main

    return data_dict


def repeat_foliate(data_commission_list: list):
    foliates = []

    for d in data_commission_list:
        foliates.append(d["foliate"])

    foliate_set = set(foliates)

    return not (len(foliates) == len(foliate_set))


def create_bulk_commissions(data_commission_list: list):
    if not repeat_foliate(data_commission_list):

        for commission in data_commission_list:
            create_register_commission_one(commission)
        return True

    return False


def create_register_commission_one(data_commission: dict):
    commission = models.Commission.objects.create(
        status=data_commission["status"],
        foliate_teacher=data_commission["foliate"],
        uri=data_commission["uri"],
        path_pdf=data_commission["path_file"],
        id_commissions=data_commission["id_commission"],
        id_teacher=data_commission["id_teacher"],
    )

    return commission


def create_teacher_ghost():
    """Function to create a register for elements no register in database"""

    try:
        models.Teachers.objects.get(id_teacher=1)
        print("Getting UNKNOWN")
        l(__name__, "Getting UNKNOWN")
    except:
        models.Teachers.objects.create(
            name="UNKNOWN", email1="email@email.com", email2="email@email.com"
        )
        print("Creating UNKNOWN")
        l(__name__, "Creating UNKNOWN")


def delete_commission(id: int) -> bool:
    """
    Delete the commission main
    """
    try:
        commission = models.Commissions.objects.get(id_commissions=id)
        name = commission.pdf_master.name.split(path.sep)[-1]
        name_pdf = path.join(BASE_DIR, "uploads", name)
        name_folder = name_pdf.replace(".pdf", "")
        delete_files(path_folder=name_folder, path_pdf=name_pdf)
        commission.delete()
        return True
    except Exception as e:
        l(
            __name__,
            message=f"El id de la comisión no existe: {id}",
            type=E,
            error=e,
        )
        print(f"El id de la comisión no existe: {id}")
        return False


def load_teachers_from_csv(rows) -> bool:
    teachers = []
    for i, row in enumerate(rows[1:]):
        columns = row.strip().split(",")

        if len(columns) > 1:
            name = columns[0].upper().strip()
            email1 = columns[1].lower().strip()
            email2 = None
            if len(columns) >= 3:
                email2 = columns[2].lower().strip() or None

            teachers.append(
                models.Teachers(name=name, email1=email1, email2=email2)
            )
    try:
        if len(teachers) > 0:
            models.Teachers.objects.bulk_create(teachers)
            return True
    except:
        return False
