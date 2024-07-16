from django.urls import path

from .views import *

urlpatterns = [
    path('dashboard/', HomeView.as_view(), name='dashboard'),
    path('assessment/<int:audit_id>', SubmitAssessmentView.as_view(), name='submit_assessment'),
    path('evidence/create/<int:question_pk>/', CreateEvidenceView.as_view(), name='evidence_create'),
    path('reports/orgs/performance/', OrganizationReportView.as_view(), name='org_performance_report'),
]
