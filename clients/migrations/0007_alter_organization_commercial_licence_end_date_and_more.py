# Generated by Django 4.2.1 on 2024-06-11 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0006_alter_department_title_ar_alter_employee_job_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='commercial_licence_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Commercial Licence End Date'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='commercial_registration_no',
            field=models.CharField(max_length=256, verbose_name='Commercial Registration Number'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='type',
            field=models.CharField(choices=[('RESTAURANTS', 'Restaurants'), ('HOTELS', 'Hotels'), ('PILGRIMS_CENTER', 'Pilgrims Center'), ('MISC', 'Miscellaneous')], max_length=128, verbose_name='Type'),
        ),
    ]
