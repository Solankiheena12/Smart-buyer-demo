# Generated by Django 4.2.3 on 2023-08-21 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("employee", "0001_initial"),
        ("user", "0008_auto_20230805_2207"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="employee_id",
        ),
        migrations.AddField(
            model_name="user",
            name="employee",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="employee.employee",
            ),
        ),
    ]
