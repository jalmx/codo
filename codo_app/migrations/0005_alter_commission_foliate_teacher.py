# Generated by Django 4.2.10 on 2024-03-03 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("codo_app", "0004_alter_commission_path_pdf"),
    ]

    operations = [
        migrations.AlterField(
            model_name="commission",
            name="foliate_teacher",
            field=models.FilePathField(max_length=20, unique=True),
        ),
    ]