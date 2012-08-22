__version__ = "2.0.1"

from django.conf import settings
if settings.configured:
	from .widgets import Select2Widget, Select2MultipleWidget, HeavySelect2Widget, HeavySelect2MultipleWidget, \
		AutoHeavySelect2Widget, AutoHeavySelect2MultipleWidget
	from .fields import Select2ChoiceField, Select2MultipleChoiceField, HeavySelect2ChoiceField, \
		HeavySelect2MultipleChoiceField, HeavyModelSelect2ChoiceField, HeavyModelSelect2MultipleChoiceField, \
		ModelSelect2Field, ModelSelect2MultipleField, AutoSelect2Field, AutoSelect2MultipleField, \
		AutoModelSelect2Field, AutoModelSelect2MultipleField 
	from .views import Select2View, NO_ERR_RESP
