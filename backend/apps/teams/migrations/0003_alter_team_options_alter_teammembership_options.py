from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("teams", "0002_teammembership"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="team",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="teammembership",
            options={"ordering": ["team__name"]},
        ),
    ]
