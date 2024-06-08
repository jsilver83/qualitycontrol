from django.urls import path

from clients import views

urlpatterns = [
    path('', views.ListOrganizationView.as_view(), name="organizations_list"),
    path('create/', views.CreateOrganizationView.as_view(), name="create_organization"),
    path('<int:org_id>', views.DetailOrganizationView.as_view(), name="view_organization"),
    path('update/<slug:pk>/', views.UpdateOrganizationView.as_view(), name="update_organization"),
    path('delete/<slug:pk>/', views.DeleteOrganizationView.as_view(), name="delete_organization"),

    path('organization/<int:org_id>/departments', views.UpdateDepartmentsView.as_view(), name="update_departments"),

    path('<int:org_id>/employees', views.ListEmployeeView.as_view(), name="employees_list"),
    path('<int:org_id>/employee/create/', views.CreateEmployeeView.as_view(), name="create_employee"),
    # path('<int:org_id>/employee/<int:org_id>', views.DetailEmployeeView.as_view(), name="view_employee"),
    path('employee/update/<slug:pk>/', views.UpdateEmployeeView.as_view(), name="update_employee"),
    path('employee/delete/<slug:pk>/', views.DeleteEmployeeView.as_view(), name="delete_employee"),

    path('task/create/<int:question_pk>/', views.CreateTaskView.as_view(), name="create_task"),
    path('tasks/', views.ListTaskView.as_view(), name="tasks_list"),
    path('task/<slug:pk>', views.DetailTaskView.as_view(), name="view_task"),
    path('task/update/<slug:pk>', views.UpdateTaskView.as_view(), name="update_task"),
    path('task/complete/<slug:pk>', views.CompleteTaskView.as_view(), name="complete_task"),
    path('task/cancel/<slug:pk>', views.CancelTaskView.as_view(), name="cancel_task"),


]

