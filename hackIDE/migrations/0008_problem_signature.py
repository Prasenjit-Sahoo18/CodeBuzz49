from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hackIDE', '0007_problem_boilerplate'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestproblem',
            name='signature_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contestproblem',
            name='signature_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='contestproblem',
            name='signature_params',
            field=models.TextField(blank=True, default='[]'),
        ),
        migrations.AddField(
            model_name='contestproblem',
            name='signature_return',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]

