// Fixes select2 initialization in Django admin inline formsets when rows are added
(function ($) {
  window.django.jQuery(document).on('formset:added', function (event, $row, formsetName) {
    $($row).find('.django-select2').djangoSelect2()
  })
})(this.jQuery)
