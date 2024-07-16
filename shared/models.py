from django.conf import settings
from django.db import models

from assessment.models import Audit
from django.utils.dateformat import format


class Report:

    @staticmethod
    def get_org_performance(org, latest_audits_count=5):
        targeted_audits = Audit.objects.filter(
            created_for=org,
            status__in=[Audit.Status.SUBMITTED, Audit.Status.DRAFT, ]
        ).order_by('-inspection_date', '-id')[:latest_audits_count]

        scores = []
        labels = []
        for audit in targeted_audits:
            scores.append(audit.weighted_total())
            labels.append(format(audit.inspection_date or audit.created_on, settings.DATE_FORMAT) + ' (#' + str(audit.pk) + ')')

        return labels, scores
