from constrainedfilefield.fields import ConstrainedFileField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _, get_language

User = settings.AUTH_USER_MODEL


class Audit(models.Model):
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
        related_name='audits',
    )

    derived_from = models.ForeignKey(
        "Audit",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Derived From'),
        related_name='driven_audits',
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
        get_user_model(),
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name=_('Created By'),
        related_name='audits',
    )

    updated_on = models.DateTimeField(
        _('Updated On'),
        auto_now=True,
        null=True,
        blank=False,
    )

    updated_by = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name=_('Updated By'),
        related_name='updated_audits',
    )
    # endregion audit

    def __str__(self):
        if get_language() == 'ar':
            return self.title_ar
        else:
            return self.title_en

    def full_score(self):
        full_score = 0
        for question in self.questions.all():
            if question.is_scored():
                full_score += question.weight()

        return full_score

    def total_score(self):
        total = 0
        for question in self.questions.all():
            if question.is_scored():
                total += question.score()

        return total

    def weighted_total(self):
        if self.full_score():
            return self.total_score() / self.full_score() * 100
    weighted_total.short_description = _('Weighted Total (%)')

    def score_in_words(self):
        return '{} out of {}'.format(self.total_score(), self.full_score())


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
    audit = models.ForeignKey(
        "Audit",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Audit'),
        related_name='questions',
    )

    prompt_ar = models.TextField(
        _('Prompt (AR)'),
        blank=True,
    )

    prompt_en = models.TextField(
        _('Prompt (EN)'),
        blank=False,
    )

    help_text_ar = models.TextField(
        _('Help Text (AR)'),
        blank=True,
    )

    help_text_en = models.TextField(
        _('Help Text (EN)'),
        blank=True,
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

    class Meta:
        ordering = ('audit', 'display_order', )

    def __str__(self):
        if get_language() == 'ar':
            return self.prompt_ar
        else:
            return self.prompt_en

    def prompt(self):
        return str(self)

    def get_the_answer(self):
        return self.answers.filter(selected_answer=True).first()

    def is_answered(self):
        return self.answers.filter(selected_answer=True).exists()
    is_answered.boolean = True
    is_answered.short_description = _('Answered?')

    def weight(self):
        return self.answers.aggregate(Max('weight')).get('weight__max', 0.0)

    def score(self):
        if self.is_answered():
            return self.get_the_answer().weight

    def is_scored(self):
        return self.score() is not None
    is_scored.boolean = True
    is_scored.short_description = _('Scored?')


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
        blank=True,
    )

    prompt_en = models.TextField(
        _('Prompt (EN)'),
        blank=False,
    )

    weight = models.FloatField(
        _('Weight'),
        null=True,
        blank=True,
        default=1,
        help_text=_('Empty wight indicate N/A answers which are not going to be calculated in the total score'),
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

    def prompt(self):
        return str(self)


class Evidence(models.Model):
    class Types(models.TextChoices):
        PICTURE = 'PICTURE', _('Picture'),
        VIDEO = 'VIDEO', _('Video'),
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
            # TODO: add video file formats like mp4 and avi
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
