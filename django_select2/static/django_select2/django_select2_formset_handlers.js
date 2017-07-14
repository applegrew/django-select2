// --*  NEW 20tab *--
(function($) {

    django.jQuery(document).on('formset:added', function (event, $row, formsetName) {
        $($row).find('.django-select2').djangoSelect2();
    });

})(this.jQuery);
// --* END NEW *--