from django.db import models
from datetime import datetime

# Create your models here.


STATUS_COMMISSION = [("C", "created"), ("P", "progress"), ("D", "done")]


class Commissions(models.Model):
    """Model for commissions Model"""

    id_commissions = models.AutoField(primary_key=True, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    date = models.DateTimeField(default=datetime.today, null=False, editable=False)
    foliate_commission = models.CharField(max_length=20, null=False, blank=False)
    pdf_master = models.FileField(null=False, blank=False, upload_to="uploads")
    status = models.CharField(
        max_length=5,
        null=False,
        choices=STATUS_COMMISSION,
        default="C",
    )

    def __str__(self) -> str:
        return f"id: {self.id_commissions} - {self.name} : {self.foliate_commission}"


class Teachers(models.Model):
    """Model for teacher Model"""

    id_teacher = models.AutoField(primary_key=True, null=False, unique=True)
    name = models.CharField(max_length=20, unique=True, null=False)
    email1 = models.EmailField(max_length=20, unique=True, null=False)
    email2 = models.EmailField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self) -> str:
        return f"id {self.id_teacher} {self.name} : {self.email1} : {self.email2 if self.email2 else ''}"


STATUS = [("S", "sended"), ("F", "fail"), ("P", "pending")]


class Commission(models.Model):

    id_commission = models.AutoField(primary_key=True, null=False, unique=True)
    status = models.CharField(max_length=1, null=False, choices=STATUS, default="P")
    foliate_teacher = models.CharField(max_length=20, null=False, unique=True)
    uri = models.CharField(max_length=255, null=False, blank=False, unique=True)
    path_pdf = models.CharField(max_length=100, null=False, unique=True, blank=True)

    id_teacher = models.ForeignKey(Teachers, on_delete=models.CASCADE)
    id_commissions = models.ForeignKey(Commissions, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"status: {self.status}; foliate teacher: {self.foliate_teacher}; Teacher: {self.id_teacher}; id commission: {self.id_commissions}; path: {self.path_pdf}"


class EmailBase(models.Model):
    id = models.AutoField(primary_key=True, unique=True, null=False)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=255, null=False)
