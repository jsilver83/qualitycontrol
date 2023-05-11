from constrainedfilefield.fields import ConstrainedFileField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _, get_language

User = settings.AUTH_USER_MODEL


class Assessment(models.Model):
    class Types(models.TextChoices):
        RESTAURANTS = 'RESTAURANTS', _('Restaurants')
        HOTELS = 'HOTELS', _('Hotels')
        MISC = 'MISC', _('Miscellaneous')

    # region fields
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

    description_ar = models.TextField(
        _('Description (AR)'),
        blank=False,
    )

    description_en = models.TextField(
        _('Description (EN)'),
        blank=False,
    )

    type = models.CharField(
        _('Type'),
        blank=False,
        max_length=128,
        choices=Types.choices,
    )

    created_for = models.ForeignKey(
        "clients.Organization",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name=_('Created For'),
        related_name='assessments',
    )

    derived_from = models.ForeignKey(
        "Assessment",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Derived From'),
        related_name='driven_assessments',
    )
    # endregion fields

    # region audit fields
    created_on = models.DateTimeField(
        _('Created On'),
        auto_now_add=True,
        null=True,
        blank=False,
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name=_('Created By'),
        related_name='assessments',
    )

    updated_on = models.DateTimeField(
        _('Updated On'),
        auto_now=True,
        null=True,
        blank=False,
    )

    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name=_('Updated By'),
        related_name='updated_assessments',
    )
    # endregion audit

    def __str__(self):
        if get_language() == 'ar':
            return self.title_ar
        else:
            return self.title_en


class Section(models.Model):
    # region fields
    title_ar = models.CharField(
        _('Title (AR)'),
        max_length=256,
        blank=False,
    )

    title_en = models.CharField(
        _('Title (EN)'),
        max_length=256,
        blank=False,
    )

    sub_of = models.ForeignKey(
        "Section",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Sub of'),
        related_name='sub_sections',
    )

    display_order = models.PositiveSmallIntegerField(
        _('Display Order'),
        null=True,
        blank=False,
    )

    show_flag = models.BooleanField(
        _('Show?'),
        default=True,
        blank=True,
    )
    # endregion fields

    def __str__(self):
        if get_language() == 'ar':
            return self.title_ar
        else:
            return self.title_en


class Question(models.Model):
    # region fields
    assessment = models.ForeignKey(
        "Assessment",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Assessment'),
        related_name='questions',
    )

    prompt_ar = models.TextField(
        _('Prompt (AR)'),
        blank=False,
    )

    prompt_en = models.TextField(
        _('Prompt (EN)'),
        blank=False,
    )

    help_text_ar = models.TextField(
        _('Help Text (AR)'),
        blank=False,
    )

    help_text_en = models.TextField(
        _('Help Text (EN)'),
        blank=False,
    )

    section = models.ForeignKey(
        "Section",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Section'),
        related_name='questions',
    )

    display_order = models.PositiveSmallIntegerField(
        _('Display Order'),
        null=True,
        blank=False,
    )
    # endregion fields

    def __str__(self):
        if get_language() == 'ar':
            return self.prompt_ar
        else:
            return self.prompt_en


class Answer(models.Model):
    # region fields
    question = models.ForeignKey(
        "Question",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Question'),
        related_name='answers',
    )

    prompt_ar = models.TextField(
        _('Prompt (AR)'),
        blank=False,
    )

    prompt_en = models.TextField(
        _('Prompt (EN)'),
        blank=False,
    )

    weight = models.FloatField(
        _('Weight'),
        null=True,
        blank=False,
        default=1,
    )

    selected_answer = models.BooleanField(
        _('Selected?'),
        default=False,
    )

    answered_on = models.DateTimeField(
        _('Answered On'),
        null=True,
        blank=True,
    )

    answered_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Answered By'),
        related_name='answers',
    )
    # endregion fields

    def __str__(self):
        if get_language() == 'ar':
            return self.prompt_ar
        else:
            return self.prompt_en


class Evidence(models.Model):
    class Types(models.TextChoices):
        PICTURE = 'PICTURE', _('Picture'),
        MISC = 'misc', _('Miscellaneous'),

    # region fields
    question = models.ForeignKey(
        'Question',
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name='list_of_evidence',
    )

    uploaded_file = ConstrainedFileField(
        null=True,
        blank=False,
        upload_to='evidence',
        content_types=[
            'application/pdf',
            'image/png',
            'image/bmp',
            'image/jpg',
            'image/jpeg',
            'image/gif',
        ],
        max_upload_size=2000000,  # 2.0 mb limit
    )

    notes = models.TextField(
        _('Notes'),
        blank=True,
    )

    type = models.CharField(
        _('Type'),
        blank=False,
        max_length=256,
        choices=Types.choices,
    )

    uploaded_on = models.DateTimeField(
        _('Uploaded On'),
        auto_now_add=True,
        null=True,
    )

    uploaded_by = models.ForeignKey(
        User,
        verbose_name=_('Uploaded By'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    # endregion fields

    def __str__(self):
        return '{} {}'.format(self.type, self.question)
