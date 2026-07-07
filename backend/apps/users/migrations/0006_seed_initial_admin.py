from django.db import migrations

from apps.users.bootstrap import seed_admin_from_env


def forwards(apps, schema_editor):
    # Historical model: seed_admin_from_env only uses update_or_create + a
    # pre-hashed password, so it works without the custom manager/methods.
    User = apps.get_model("users", "User")
    seed_admin_from_env(User)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0005_alter_user_managers"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
