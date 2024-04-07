from django.conf import settings

from codo_app import models
from codo_app.util.log import l


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


def create_bulk_commissions(data_commission_list: list):

    for commission in data_commission_list:
        create_register_commission_one(commission)

    return True


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
