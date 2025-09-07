from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hackIDE', '0005_proctoringsession'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestproblem',
            name='boilerplate_code',
            field=models.TextField(default='{}'),
        ),
    ]

