# Generated by Django 4.2.1 on 2023-05-11 09:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=256, verbose_name='Name (AR)')),
                ('name_en', models.CharField(max_length=256, verbose_name='Name (EN)')),
                ('type', models.CharField(choices=[('RESTAURANTS', 'Restaurants'), ('HOTELS', 'Hotels'), ('MISC', 'Miscellaneous')], max_length=128, verbose_name='Type')),
                ('city', models.CharField(help_text='Which city is this organization located in?', max_length=128, verbose_name='City')),
                ('address', models.TextField(blank=True, verbose_name='Address')),
                ('website', models.URLField(blank=True, verbose_name='Website')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name_ar', models.CharField(blank=True, max_length=256, verbose_name='First Name (AR)')),
                ('first_name_en', models.CharField(max_length=256, verbose_name='First Name (EN)')),
                ('last_name_ar', models.CharField(blank=True, max_length=256, verbose_name='Last Name (AR)')),
                ('last_name_en', models.CharField(max_length=256, verbose_name='Last Name (EN)')),
                ('job_title', models.CharField(choices=[('CEO', 'CEO'), ('MANAGER', 'Manager'), ('SUPERVISOR', 'Supervisor'), ('OTHER', 'Other')], max_length=128, verbose_name='Job Title')),
                ('nationality', django_countries.fields.CountryField(max_length=2, verbose_name='Nationality')),
                ('mobile', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='Mobile')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Associated User')),
            ],
        ),
    ]
