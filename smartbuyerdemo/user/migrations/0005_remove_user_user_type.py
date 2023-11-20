from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0004_alter_user_user_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="user_type",
        ),
    ]
