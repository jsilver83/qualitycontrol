from django.urls import path

from assessment import views

urlpatterns = [
    path('', views.ListAuditView.as_view(), name="assessments_list"),
    path('create/', views.CreateAssessmentView.as_view(), name="create_assessment"),
    path('<int:audit_id>/derive/', views.CreateAssessmentView.as_view(), name="derive_assessment"),
    path('<int:audit_id>/view/', views.DetailAssessmentView.as_view(), name="view_assessment"),
    path('<int:audit_id>/export/', views.DetailAssessmentExportView.as_view(), name="export_assessment"),
    path('<int:audit_id>/info/', views.AssessmentInfoView.as_view(), name="assessment_info"),


    path('<int:audit_id>/questions/', views.ListQuestionView.as_view(), name="questions"),
    path('<int:audit_id>/question/create', views.CreateQuestionView.as_view(), name="create_question"),
    path('<int:audit_id>/question/<int:question_id>/update', views.UpdateQuestionView.as_view(), name="update_question"),
    path('<int:audit_id>/question/<int:question_id>', views.DetailQuestionView.as_view(), name="view_question"),
    path('question/<slug:pk>/delete', views.DeleteQuestionView.as_view(), name="delete_question"),

    path('section/create/', views.CreateSectionView.as_view(), name="create_section"),


]