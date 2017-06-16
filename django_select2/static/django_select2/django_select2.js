(function($) {
    var init = function($element, options) {
        $element.select2(options);
    };

    var initHeavy = function($element, options) {
        var settings = $.extend({
            ajax: {
                data: function(params) {
                    var result = {
                        term: params.term,
                        page: params.page,
                        field_id: $element.data('field_id')
                    };

                    var dependentFields = $element.data('select2-dependent-fields');
                    if (dependentFields) {
                        dependentFields = dependentFields.trim().split(/\s+/);
                        $.each(dependentFields, function(i, dependentField) {
                            result[dependentField] = $('[name=' + dependentField + ']', $element.closest('form')).val();
                        });
                    }

                    return result;
                },
                processResults: function(data, page) {
                    return {
                        results: data.results,
                        pagination: {
                            more: data.more
                        }
                    };
                }
            }
        }, options);

        $element.select2(settings);
    };

    $.fn.djangoSelect2 = function(options) {
        var settings = $.extend({}, options);
        $.each(this, function(i, element) {
            var $element = $(element);
            if ($element.hasClass('django-select2-heavy')) {
                initHeavy($element, settings);
                // --* NEW 20tab *--
                $selected_option = $element.find(':selected');
                if ($selected_option.val() & !$selected_option.text()) {
                    $.ajax({
                        type: $element.data('ajax--type'),
                        url: $element.data('ajax--url') + $selected_option.val(),
                        dataType: 'json'
                    }).then(function (data) {
                        $selected_option.text(data.text);
                        $selected_option.removeData();
                        $element.trigger('change');
                    });
                }
                // --* END NEW *--
            } else {
                init($element, settings);
            }
        });
        return this;
    };

    $(function() {
        // --* CHANGED 20tab *--
        $('.django-select2').not('.empty-form .django-select2').djangoSelect2();
        // --* END CHANGED *---
    });

    // --*  NEW 20tab *--
    django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
        $($row).find('.django-select2').djangoSelect2();
    });
    // --* END NEW *--

}(this.jQuery));
