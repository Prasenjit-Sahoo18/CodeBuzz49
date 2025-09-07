from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hackIDE', '0008_problem_signature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestproblem',
            name='contest',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='problems', to='hackIDE.contest'),
        ),
    ]

