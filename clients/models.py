from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class Organization(models.Model):
    class Types(models.TextChoices):
        RESTAURANTS = 'RESTAURANTS', _('Restaurants')
        HOTELS = 'HOTELS', _('Hotels')
        MISC = 'MISC', _('Miscellaneous')

    # region fields
    name_ar = models.CharField(
        _('Name (AR)'),
        max_length=256,
        blank=False,
    )

    name_en = models.CharField(
        _('Name (EN)'),
        max_length=256,
        blank=False,
    )

    type = models.CharField(
        _('Type'),
        blank=False,
        max_length=128,
        choices=Types.choices,
    )

    city = models.CharField(
        _('City'),
        blank=False,
        max_length=128,
        help_text=_('Which city is this organization located in?')
    )

    address = models.TextField(
        _('Address'),
        blank=True,
    )

    website = models.URLField(
        _('Website'),
        blank=True,
    )
    # endregion fields


class Department(models.Model):
    # region fields
    organization = models.ForeignKey(
        "Organization",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Department'),
        related_name='departments',
    )

    title_ar = models.CharField(
        _('Title (AR)'),
        max_length=512,
        blank=False,
    )

    title_en = models.CharField(
        _('Title (EN)'),
        max_length=512,
        blank=False,
    )
    # endregion fields


class Employee(models.Model):
    class JobTitles(models.TextChoices):
        CEO = 'CEO', _('CEO')
        OWNER = 'OWNER', _('Owner')
        MANAGER = 'MANAGER', _('Manager')
        DEPARTMENT_HEAD = 'DEPARTMENT_HEAD', _('Department Head')
        SUPERVISOR = 'SUPERVISOR', _('Supervisor')
        SECRETARY = 'SECRETARY', _('Secretary')
        COOK = 'COOK', _('Cook')
        WORKER = 'WORKER', _('Worker')
        OTHER = 'OTHER', _('Other')

    # region fields
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Associated User'),
    )

    first_name_ar = models.CharField(
        _('First Name (AR)'),
        max_length=256,
        blank=True,
    )

    first_name_en = models.CharField(
        _('First Name (EN)'),
        max_length=256,
        blank=False,
    )

    last_name_ar = models.CharField(
        _('Last Name (AR)'),
        max_length=256,
        blank=True,
    )

    last_name_en = models.CharField(
        _('Last Name (EN)'),
        max_length=256,
        blank=False,
    )

    job_title = models.CharField(
        _('Job Title'),
        blank=False,
        max_length=128,
        choices=JobTitles.choices,
    )

    department = models.ForeignKey(
        "Department",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Department'),
        related_name='employees',
    )

    nationality = CountryField(
        _('Nationality'),
        blank=False,
    )

    mobile = PhoneNumberField(
        blank=True,
        verbose_name=_('Mobile'),
    )
    # endregion fields
