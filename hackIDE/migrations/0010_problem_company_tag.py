from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hackIDE', '0009_problem_contest_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestproblem',
            name='company_tag',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]

