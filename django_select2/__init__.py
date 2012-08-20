__version__ = "2.0"

from django.conf import settings
if settings.configured:
	from .widgets import Select2Widget, Select2MultipleWidget, HeavySelect2Widget, HeavySelect2MultipleWidget, AutoHeavySelect2Widget
	from .fields import Select2ChoiceField, Select2MultipleChoiceField, \
		HeavySelect2ChoiceField, HeavySelect2MultipleChoiceField, \
		ModelSelect2Field, AutoSelect2Field, AutoModelSelect2Field, ModelMultipleSelect2Field
	from .views import Select2View, NO_ERR_RESP
