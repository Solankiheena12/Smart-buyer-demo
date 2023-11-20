# Generated by Django 3.2.9 on 2023-08-05 16:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_attachment'),
        ('vendor', '0001_initial'),
        ('user', '0007_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='company.company'),
        ),
        migrations.AddField(
            model_name='user',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='vendor.vendor'),
        ),
    ]
