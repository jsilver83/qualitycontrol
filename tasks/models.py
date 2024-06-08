from constrainedfilefield.fields import ConstrainedFileField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _, get_language


class Task(models.Model):
    # region fields
    description_ar = models.TextField(
        _('Description (AR)'),
        blank=True,
    )

    description_en = models.TextField(
        _('Description (EN)'),
        blank=False,
    )

    assigned_employee = models.ForeignKey(
        "clients.Employee",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name=_('Assigned Employee'),
        related_name='assigned_tasks',
    )

    question = models.ForeignKey(
        "assessment.Question",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Question'),
        related_name='tasks',
    )

    due_date = models.DateTimeField(
        _('Due Date'),
        null=True,
        blank=False,
    )

    completion_date = models.DateTimeField(
        _('Completion Date'),
        null=True,
        blank=True,
    )

    completed_by = models.ForeignKey(
        "clients.Employee",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Completed By'),
        related_name='completed_tasks',
    )

    supporting_documents = ConstrainedFileField(
        verbose_name=_('Supporting Documents'),
        null=True,
        blank=True,
        upload_to='tasks/supporting_docs',
        content_types=[
            'application/pdf',
            'image/png',
            'image/bmp',
            'image/jpg',
            'image/jpeg',
            'image/gif',
        ],
        max_upload_size=2000000,  # 2.0 mb limit
        help_text=_('Upload any documents that shall help the assigned personnel to accomplish the task'),
    )

    completion_evidence = ConstrainedFileField(
        verbose_name=_('Completion Evidence'),
        null=True,
        blank=True,
        upload_to='tasks/completion_evidence',
        content_types=[
            'application/pdf',
            'image/png',
            'image/bmp',
            'image/jpg',
            'image/jpeg',
            'image/gif',
        ],
        max_upload_size=2000000,  # 2.0 mb limit
        help_text=_('Upload any documents that prove that the task was completed successfully'),
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
        related_name='created_tasks',
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
        related_name='updated_tasks',
    )
    # endregion audit

    def description(self):
        if get_language() == 'ar':
            return self.description_ar or self.description_en or ''
        else:
            return self.description_en or self.description_ar or ''

    def __str__(self):
        return '{} {} {}'.format(self.assigned_employee, self.question, self.description())
