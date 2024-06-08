from .models import Audit, Section, Question


class AssessmentServices():

    def __int__(self, audit):
        self.audit = audit

    def add_root_section(self):
        self.audit.root_section = Section.add_root(instance=Section(
            title_en=self.audit.title_en,
            title_ar=self.audit.title_ar,
            display_order=1)
        )

    def derive_sections(self):
        derived_from_sections = Section.dump_bulk(parent=self.audit.derived_from.root_section)
        derived_from_sections_without_root = derived_from_sections[0]["children"]
        Section.load_bulk(bulk_data=derived_from_sections_without_root, parent=self.audit.root_section)

    def derive_questions(self):
        derived_from_questions = self.derived_from.questions.all()
        for question in derived_from_questions:
            question.pk = None
            question.audit = self.audit
            question.section = self.audit.root_section.get_descendants().filter(title_en=question.title_en)
            answers = question.answers.all()
            question.save()
            for answer in answers:
                answer.pk = None
                answer.question = question
                answer.save()

    def derive_audit(self):
        self.add_root_section(self)
        self.derive_sections(self)
        self.derive_questions()
