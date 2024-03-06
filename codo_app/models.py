from django.db import models
from datetime import datetime

# Create your models here.


class Commissions(models.Model):
    """ Model for commissions Model
    """
    _id_commissions = models.AutoField(primary_key=True,
                                       unique=True,
                                       null=False)
    name = models.CharField(max_length=255, null=False)
    date = models.DateTimeField(default=datetime.today, null=False)
    foliate_commission = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.name} : {self.foliate_commission}"


class Teachers(models.Model):
    """ Model for teacher Model
    """

    _id_teacher = models.AutoField(primary_key=True, null=False, unique=True)
    name = models.CharField(max_length=20, unique=True, null=False)
    email1 = models.EmailField(max_length=20, unique=True, null=False)
    email2 = models.EmailField(max_length=20,
                               unique=True,
                               blank=True,
                               null=True)

    def __str__(self) -> str:
        return f"{self.name} : {self.email1} : {self.email2 if self.email2 else ''}"


STATUS = [("S", "sended"), ("F", "fail"), ("P", "pending")]


class Commission(models.Model):

    status = models.CharField(max_length=1,
                              null=False,
                              choices=STATUS,
                              default="P")
    foliate_teacher = models.CharField(max_length=20, null=False, unique=True)
    # path_pdf = models.FilePathField(null=False, unique=True, blank=True)
    path_pdf = models.CharField(max_length=100,
                                null=False,
                                unique=True,
                                blank=True)
    _id_teacher = models.ForeignKey(Teachers, on_delete=models.CASCADE)
    _id_commission = models.ForeignKey(Commissions, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"status: {self.status}; foliate teacher: {self.foliate_teacher}; Teacher: {self._id_teacher}; id commission: {self._id_commission}; path: {self.path_pdf}"