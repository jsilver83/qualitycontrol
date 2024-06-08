from constrainedfilefield.fields import ConstrainedFileField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _, get_language
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.signals import user_logged_in


class Organization(models.Model):
    class Types(models.TextChoices):
        RESTAURANTS = 'RESTAURANTS', _('Restaurants')
        HOTELS = 'HOTELS', _('Hotels')
        MISC = 'MISC', _('Miscellaneous')

    # region fields
    name_ar = models.CharField(
        _('Name (AR)'),
        max_length=256,
        blank=True,
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

    commercial_registration_no = models.CharField(
        _('Commercial Registration Number'),
        blank=False,
        max_length=256,
        unique=True,
    )

    commercial_licence = ConstrainedFileField(
        verbose_name=_('Commercial Licence'),
        null=True,
        blank=False,
        upload_to='licences',
        content_types=[
            'application/pdf',
            'image/png',
            'image/bmp',
            'image/jpg',
            'image/jpeg',
            'image/gif',
        ],
        max_upload_size=2048000,  # 2.0 mb limit
    )

    commercial_licence_end_date = models.DateField(
        _('Commercial Licence End Date'),
        null=True,
        blank=False,
    )

    logo = ConstrainedFileField(
        verbose_name=_('Logo'),
        null=True,
        blank=True,
        upload_to='logos',
        content_types=[
            'image/png',
            'image/bmp',
            'image/jpg',
            'image/jpeg',
            'image/gif',
        ],
        max_upload_size=512000,  # 0.5 mb limit
    )

    address = models.TextField(
        _('Address'),
        blank=True,
    )

    address_on_map = models.TextField(
        _('Address on Map'),
        blank=True,
    )

    website = models.URLField(
        _('Website'),
        blank=True,
    )
    # endregion fields

    def __str__(self):
        if get_language() == 'ar':
            return '{} ({})'.format(self.name_ar, self.get_type_display())
        else:
            return '{} ({})'.format(self.name_en, self.get_type_display())


class Department(models.Model):
    # region fields
    organization = models.ForeignKey(
        "Organization",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Organization'),
        related_name='departments',
    )

    title_ar = models.CharField(
        _('Title (AR)'),
        max_length=512,
        blank=True,
    )

    title_en = models.CharField(
        _('Title (EN)'),
        max_length=512,
        blank=False,
    )
    # endregion fields

    def title(self):
        if get_language() == 'ar':
            return self.title_ar
        else:
            return self.title_en

    def __str__(self):
        if get_language() == 'ar':
            return self.title_ar
        else:
            return self.title_en


class Employee(models.Model):
    class JobTitles(models.TextChoices):
        CEO = 'CEO', _('CEO')
        OWNER = 'OWNER', _('Owner')
        HR = 'HR', _('HR')
        MANAGER = 'MANAGER', _('Manager')
        DEPARTMENT_HEAD = 'DEPARTMENT_HEAD', _('Department Head')
        SUPERVISOR = 'SUPERVISOR', _('Supervisor')
        SECRETARY = 'SECRETARY', _('Secretary')
        COOK = 'COOK', _('Cook')
        WORKER = 'WORKER', _('Worker')
        OTHER = 'OTHER', _('Other')

    # region fields
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Associated User'),
        related_name='employee',
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

    manager = models.ForeignKey(
        'Employee',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Manager'),
        related_name='responsible_for',
    )

    personal_picture = ConstrainedFileField(
        verbose_name=_('Personal Picture'),
        null=True,
        blank=True,
        upload_to='employees',
        content_types=[
            'image/png',
            'image/bmp',
            'image/jpg',
            'image/jpeg',
            'image/gif',
        ],
        max_upload_size=512000,  # 0.5 mb limit
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


    @property
    def organization(self):
        return self.department.organization

    def has_owner_permissions(self):
        return self.job_title in [self.JobTitles.OWNER, self.JobTitles.CEO, self.JobTitles.HR]


    def first_name(self):
        if get_language() == 'ar':
            return '{}'.format(self.first_name_ar)
        else:
            return '{}'.format(self.first_name_en)

    def last_name(self):
        if get_language() == 'ar':
            return '{}'.format(self.last_name_ar)
        else:
            return '{}'.format(self.last_name_en)

    def full_name(self):
        if get_language() == 'ar':
            return '{} {}'.format(self.first_name_ar, self.last_name_ar)
        else:
            return '{} {}'.format(self.first_name_en, self.last_name_en)

    def __str__(self):
        if get_language() == 'ar':
            return '{} {}'.format(self.first_name_ar, self.last_name_ar)
        else:
            return '{} {}'.format(self.first_name_en, self.last_name_en)


class Task(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', _('New')
        DONE = 'DONE', _('Done')
        CANCELLED = 'CANCELLED', _('Cancelled')

    # region fields

    employee = models.ForeignKey(
        "Employee",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Employee'),
        related_name='employee_tasks',
    )

    question = models.ForeignKey(
        "assessment.Question",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Question'),
        related_name='question_tasks',
    )

    description = models.TextField(
        _('Task Description'),
        max_length=512,
        blank=False,
    )

    create_date = models.DateField(
        _('Create Date'),
        null=True,
        blank=False,
    )

    due_date = models.DateField(
        _('Due Date'),
        null=True,
        blank=False,
    )

    status = models.CharField(
        _('Status'),
        blank=False,
        max_length=128,
        choices=Status.choices,
    )

    attachment = ConstrainedFileField(
        null=True,
        blank=True,
        upload_to='tasks',
        content_types=[
            'application/pdf',
        ],
        max_upload_size=2000000,  # 2.0 mb limit
    )

    notes = models.TextField(
        _('Notes'),
        max_length=512,
        blank=True,
    )
    # endregion fields

    def __str__(self):
        return self.description


def create_user_employee(sender, user, request, **kwargs):
    try:
        employee = Employee.objects.get(user=user)
    except:
        employee = None

    if not employee:
        return Employee.objects.create(
            user=user,
            department=Department.objects.get_or_create(
                title_en='default',
                organization=Organization.objects.get_or_create(name_en='default')[0])[0])
    else:
        if not employee.department:
            return Department.objects.create(
                title_en='default',
                organization=Organization.objects.get_or_create(name_en='default')[0])


user_logged_in.connect(create_user_employee)


