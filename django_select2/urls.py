from django.conf.urls.defaults import *

from .views import AutoResponseView

urlpatterns = patterns("",
	url(r"^fields/auto.json$", AutoResponseView.as_view(), name="django_select2_central_json"),
)
