from constrainedfilefield.fields import ConstrainedFileField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Max, Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, get_language
from pyexcel_xlsx import get_data
import json

from assessment.utils import full_score, total_score

User = settings.AUTH_USER_MODEL


class Section(models.Model):
    # region fields
    title_ar = models.CharField(
        _('Title (AR)'),
        max_length=256,
        blank=True,
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
        blank=True,
    )

    show_flag = models.BooleanField(
        _('Show?'),
        default=True,
        blank=True,
    )

    # endregion fields

    class Meta:
        ordering = ('display_order', 'title_ar', 'title_en')

    @property
    def root_section(self):
        root_section = self
        while root_section.sub_of:
            root_section = root_section.sub_of
        return root_section

    def full_path(self, with_root=True):
        section = self
        full_path = section.title()
        while section.sub_of:
            if not with_root:
                if section.sub_of.sub_of:
                    full_path = section.sub_of.title() + " | " + full_path
            else:
                full_path = section.sub_of.title() + " | " + full_path
            section = section.sub_of

        return full_path

    def questions_of_subsections(self, audit):
        all_sub_sections = Section.objects.filter(Q(sub_of=self)
                                                  | Q(sub_of__sub_of=self)
                                                  | Q(sub_of__sub_of__sub_of=self))

        return Question.objects.filter(audit=audit, section__in=all_sub_sections)

    def full_score(self, audit):
        return full_score(self.questions_of_subsections(audit=audit))

    def total_score(self, audit):
        return total_score(self.questions_of_subsections(audit=audit))

    def weighted_total(self, audit):
        if self.full_score(audit=audit):
            return self.total_score(audit) / self.full_score(audit) * 100

    weighted_total.short_description = _('Weighted Total (%)')

    def score_in_words(self, audit):
        return _('{total_score} out of {full_score}').format(
            total_score=self.total_score(audit),
            full_score=self.full_score(audit),
        )

    def __str__(self):
        if get_language() == 'ar':
            return self.title_ar or self.title_en or ''
        else:
            return self.title_en or self.title_ar or ''

    def title(self):
        return str(self)


class Audit(models.Model):
    class Types(models.TextChoices):
        RESTAURANTS = 'RESTAURANTS', _('Restaurants')
        HOTELS = 'HOTELS', _('Hotels')
        PILGRIMS_CENTER = 'PILGRIMS_CENTER', _('Pilgrims Center')
        MISC = 'MISC', _('Miscellaneous')

    class Status(models.TextChoices):
        TEMPLATE = 'TEMPLATE', _('Template')
        DRAFT = 'DRAFT', _('Draft')
        SUBMITTED = 'SUBMITTED', _('Submitted')

    # region fields
    title_ar = models.CharField(
        _('Title (AR)'),
        max_length=512,
        blank=True,
        help_text=_('Write a meaningful and descriptive title (or name) for this audit in Arabic.'),
    )

    title_en = models.CharField(
        _('Title (EN)'),
        max_length=512,
        blank=False,
        unique=False,
        help_text=_('Write a meaningful and descriptive title (or name) for this audit in English.'),
    )

    description_ar = models.TextField(
        _('Description (AR)'),
        blank=True,
    )

    description_en = models.TextField(
        _('Description (EN)'),
        blank=True,
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

    inspection_date = models.DateTimeField(
        _('Inspection Date'),
        blank=True,
        null=True,
        help_text=_('Date/time of the inspection visit'),
    )

    derived_from = models.ForeignKey(
        "Audit",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Derived From'),
        related_name='driven_audits',
    )

    status = models.CharField(
        _('Status'),
        blank=False,
        max_length=128,
        choices=Status.choices,
        default="DRAFT",
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
            return self.title_ar or self.title_en or ''
        else:
            return self.title_en or self.title_ar or ''

    def title(self):
        return str(self)

    @cached_property
    def full_score(self):
        return full_score(self.questions.all())

    @cached_property
    def total_score(self):
        return total_score(self.questions.all())

    @cached_property
    def weighted_total(self):
        if self.full_score:
            return self.total_score / self.full_score * 100
        else:
            return 0

    weighted_total.short_description = _('Weighted Total (%)')

    @cached_property
    def score_in_words(self):
        from django.contrib.humanize.templatetags.humanize import number_format
        return '{} / {} (%{})'.format(self.total_score, self.full_score,
                                      number_format(self.weighted_total, decimal_pos=2))

    def get_sections(self):
        root_sections = {}
        all_sections = Question.objects.filter(audit=self).order_by('section').values_list('section',
                                                                                           flat=True).distinct()
        for section_id in all_sections:
            section = Section.objects.get(pk=section_id)
            section.score = section.score_in_words(audit=self)
            section.full_path = section.full_path(with_root=False)
            section.root_section.score = section.root_section.score_in_words(self)
            if section.root_section not in root_sections.keys():
                root_sections[section.root_section] = [section]
            else:
                root_sections[section.root_section].append(section)

        return root_sections

    def questions_count(self):
        return self.questions.count()


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
        blank=True,
    )

    is_bonus = models.BooleanField(
        _('Is a Bonus Question?'),
        default=False,
    )

    # endregion fields

    class Meta:
        ordering = ('audit', 'section', 'display_order', 'prompt_ar', 'prompt_en', )

    def __str__(self):
        if get_language() == 'ar':
            return self.prompt_ar or self.prompt_en or ''
        else:
            return self.prompt_en or self.prompt_ar or ''

    def prompt(self):
        return str(self)

    prompt.short_description = _('Prompt')

    def help_text(self):
        if get_language() == 'ar':
            return self.help_text_ar
        else:
            return self.help_text_en

    def get_the_answer(self):
        if self.answers.filter(selected_answer=True).exists():
            return self.answers.filter(selected_answer=True).first()

    get_the_answer.short_description = _('Selected Answer')

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

    def answered_by(self):
        answer = self.get_the_answer()
        if answer:
            return answer.answered_by

    def answered_on(self):
        answer = self.get_the_answer()
        if answer:
            return answer.answered_on

    def change_the_answer(self, the_new_answer, answerer):
        all_other_selected_answers = self.answers.filter(
            selected_answer=True,
        ).exclude(pk=the_new_answer.pk)

        if all_other_selected_answers:
            all_other_selected_answers.update(
                answered_by=None,
                answered_on=None,
                selected_answer=False,
            )

        if not the_new_answer.selected_answer:
            the_new_answer.answered_by = answerer
            the_new_answer.answered_on = timezone.now()
            the_new_answer.selected_answer = True
            the_new_answer.save()

    def evidences(self):
        return self.list_of_evidence.filter(type__in=[
            Evidence.Types.VIDEO,
            Evidence.Types.PICTURE,
            Evidence.Types.MISC,
        ])

    def notes(self):
        return self.list_of_evidence.filter(type__in=[
            Evidence.Types.TEXT_NOTE,
        ])


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

    prompt_ar = models.CharField(
        _('Prompt (AR)'),
        blank=True,
        max_length=256,
    )

    prompt_en = models.CharField(
        _('Prompt (EN)'),
        blank=False,
        max_length=256,
    )

    weight = models.FloatField(
        _('Weight'),
        null=True,
        blank=True,
        help_text=_('Empty wight indicate N/A answers which are not going to be calculated in the total score'),
    )

    selected_answer = models.BooleanField(
        _('Selected?'),
        default=False,
    )

    display_order = models.PositiveSmallIntegerField(
        _('Display Order'),
        null=True,
        blank=True,
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

    class Meta:
        ordering = ('question', 'display_order', '-weight',)

    def __str__(self):
        if get_language() == 'ar':
            return self.prompt_ar or self.prompt_en or ''
        else:
            return self.prompt_en or self.prompt_ar or ''

    def prompt(self):
        return str(self)

    def is_best_answer(self):
        if self.weight:
            return self.weight == self.question.weight()


class Evidence(models.Model):
    class Types(models.TextChoices):
        PICTURE = 'PICTURE', _('Picture'),
        VIDEO = 'VIDEO', _('Video'),
        TEXT_NOTE = 'TEXT_NOTE', _('Note (Text only)')
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
        verbose_name=_('Attachment'),
        null=True,
        blank=True,
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


class AuditFile(models.Model):
    audit = models.ForeignKey(
        "Audit",
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        verbose_name=_('Audit'),
        related_name='files',
    )
    filename = models.FileField(max_length=512, upload_to='uploads/')

    def multi_section(self):
        data = get_data(self.filename.file)
        print(json.dumps(data["Checklist"][0][4]))
        for row in data["Checklist"]:
            if len(row) == 5:

                main_section, c_main = Section.objects.get_or_create(title_ar=row[0])
                sub_section, c_sub = Section.objects.get_or_create(title_ar=row[1])
                if c_sub:
                    sub_section.sub_of = main_section
                    sub_section.save()

                # section = Section.objects.filter(title_en=row[2]).first()
                # if not section:
                #     section2 = Section.objects.filter(title_en=row[1]).first()
                #     if not section2:
                #         section1 = Section.objects.filter(title_en=row[0]).first()
                #         if not section1:
                #             section1 = Section.objects.create(title_en=row[0], title_ar=row[0])
                #         if row[0] != row[1]:
                #             section2 = Section.objects.create(title_en=row[1], title_ar=row[1], sub_of=section1)
                #         else:
                #             section2 = section1
                #     if row[2] != row[1]:
                #         section = Section.objects.create(title_en=row[2], title_ar=row[2], sub_of=section2)
                #     else:
                #         section = section2

                q = Question.objects.create(
                    prompt_en=row[3], prompt_ar=row[2], section=sub_section, audit=self.audit)

                Answer.objects.create(
                    question=q,
                    prompt_en="Yes",
                    prompt_ar="Yes",
                    weight=1,
                )

                Answer.objects.create(
                    question=q,
                    prompt_en="No",
                    prompt_ar="No",
                    weight=0,
                )

                Answer.objects.create(
                    question=q,
                    prompt_en="N/A",
                    prompt_ar="N/A",
                    weight=None,
                )

    def multi_section_old(self):
        data = get_data(self.filename.file)
        print(json.dumps(data["Checklist"][0][4]))
        for row in data["Checklist"]:
            if len(row) == 5:

                section = Section.objects.filter(title_en=row[2]).first()
                if not section:
                    section2 = Section.objects.filter(title_en=row[1]).first()
                    if not section2:
                        section1 = Section.objects.filter(title_en=row[0]).first()
                        if not section1:
                            section1 = Section.objects.create(title_en=row[0], title_ar=row[0])
                        if row[0] != row[1]:
                            section2 = Section.objects.create(title_en=row[1], title_ar=row[1], sub_of=section1)
                        else:
                            section2 = section1
                    if row[2] != row[1]:
                        section = Section.objects.create(title_en=row[2], title_ar=row[2], sub_of=section2)
                    else:
                        section = section2

                q = Question.objects.create(prompt_en=row[3], section=section, audit=self.audit)
                answer1 = Answer()
                answer1.question = q
                answer1.prompt_en = "Yes"
                answer1.weight = 2
                answer1.selected_answer = row[4] == 2
                answer1.save()
                answer2 = Answer()
                answer2.question = q
                answer2.prompt_en = "No"
                answer2.weight = 0
                answer2.selected_answer = row[4] == 0
                print(row[4] == 0)
                answer2.save()

    def one_section(self):
        data = get_data(self.filename.file)
        print(json.dumps(data))
        for row in data["Checklist"]:
            if len(row) > 2:
                sections = Section.objects.filter(title_en=row[0])
                if len(sections) == 0:
                    section = Section.objects.create(title_en=row[0])
                else:
                    section = sections[0]

                q = Question.objects.create(prompt_en=row[1], section=section, audit=self.audit)
                answer1 = Answer()
                answer1.question = q
                answer1.prompt_en = "Yes"
                answer1.weight = 2
                answer1.selected_answer = row[2] == 2
                answer1.save()
                answer2 = Answer()
                answer2.question = q
                answer2.prompt_en = "No"
                answer2.weight = 0
                answer2.selected_answer = row[2] == 0
                answer2.save()

    def import_excel(self):
        from openpyxl import Workbook, load_workbook
        from shared.utils import remove_bullet_numbering

        workbook = load_workbook(filename=self.filename.file)
        data = get_data(self.filename.file)
        sheet_data = data[workbook.sheetnames[0]]

        # audit = Audit.objects.create(
        #     title_ar='{} - {}'.format(workbook.sheetnames[0], remove_bullet_numbering(sheet_data[2][0], ":")),
        #     title_en='{} - {}'.format(workbook.sheetnames[0], remove_bullet_numbering(sheet_data[2][0], ":")),
        #     type=Audit.Types.PILGRIMS_CENTER,
        #     status=Audit.Status.DRAFT,
        #     created_for=None,
        # )

        for i in range(7, len(sheet_data)-1):
            row = sheet_data[i]
            if len(row) >= 4:
                main_section, c_main = Section.objects.get_or_create(title_ar=remove_bullet_numbering(row[0]))
                sub_section, c_sub = Section.objects.get_or_create(title_ar=remove_bullet_numbering(row[1]))
                if c_sub:
                    sub_section.sub_of = main_section
                    sub_section.save()

                if workbook.worksheets[0].cell(i+1, 3).fill.fgColor.rgb in ["FFA0D565", "FF92D050"]:
                    is_bonus = True
                else:
                    is_bonus = False

                q = Question.objects.create(
                    prompt_ar=remove_bullet_numbering(row[2]),
                    prompt_en=remove_bullet_numbering(row[2]),
                    section=sub_section,
                    audit=self.audit,
                    is_bonus=is_bonus,
                )

                Answer.objects.create(
                    question=q,
                    prompt_en="Compliant",
                    prompt_ar="ممتثل",
                    weight=1,
                    selected_answer=row[3] == "ممتثل",
                )

                Answer.objects.create(
                    question=q,
                    prompt_en="Non-Compliant",
                    prompt_ar="غير ممتثل",
                    weight=0,
                    selected_answer=row[3] == "غير ممتثل",
                )

                Answer.objects.create(
                    question=q,
                    prompt_en="N/A",
                    prompt_ar="N/A",
                    weight=None,
                    selected_answer=row[3] == "لا ينطبق",
                )
            else:
                break

    def save(self):
        self.import_excel()
        return super(AuditFile, self).save()
