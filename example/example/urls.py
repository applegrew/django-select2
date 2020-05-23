from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.BookCreateView.as_view(), name="book-create"),
    path("select2/", include("django_select2.urls")),
    path("admin/", admin.site.urls),
]
