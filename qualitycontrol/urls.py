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
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView

urlpatterns = i18n_patterns(
    path("select2/", include("django_select2.urls")),

    path("", RedirectView.as_view(url=reverse_lazy("dashboard")), name="home"),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', LoginView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('admin/', admin.site.urls),
    path('assessment/', include('assessment.urls')),
    path('client/', include('clients.urls')),
    path('main/', include('shared.urls')),
    prefix_default_language=True,
)

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
    path("__debug__/", include("debug_toolbar.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls'))
    ]
