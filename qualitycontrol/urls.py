"""
URL configuration for qualitycontrol project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import path, include

from shared.views import HomeView, CreateEvidenceView

urlpatterns = i18n_patterns(
    path('', HomeView.as_view(), name='home'),
    path('evidence/create/<int:question_pk>/', CreateEvidenceView.as_view(), name='evidence_create'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', LoginView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('admin/', admin.site.urls),
    prefix_default_language=False,
)

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
