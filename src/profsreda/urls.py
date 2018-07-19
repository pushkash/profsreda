"""profsreda URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from heroes import views as hero_view

urlpatterns = [
    path('', hero_view.home),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('profile/', hero_view.profile),
    path('profile/random/', hero_view.profile_random),
    path('accounts/profile/', hero_view.profile, name="account_profile"),
    path('accounts/profile/random/', hero_view.profile_random),
    path('accounts/profile/item/<int:item_pk>/', hero_view.profile_item),
    path('signup/', hero_view.customProfileCreation, name="signup"),
    path("tests/", include("tests.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
