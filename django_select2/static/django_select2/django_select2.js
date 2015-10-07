(function ($) {

    var init = function ($el, options) {
        $el.select2(options);
        return $el;
    };

    var initHeavy = function ($el, options) {
        var settings = $.extend({
            ajax: {
                data: function (params) {
                    return {
                        term: params.term,
                        page: params.page,
                        field_id: $el.data('field_id')
                    };
                },
                processResults: function (data, page) {
                    return {
                        results: data.results,
                        pagination: {
                            more: data.more
                        }
                    };
                }
            }
        }, options);

        $el.select2(settings);
        return $el;
    };

    $.fn.djangoSelect2 = function (options) {
        var settings = $.extend({}, options);
        var heavy = $(this).hasClass('django-select2-heavy');
        if (heavy) {
            return initHeavy(this, settings);
        }
        return init(this, settings);
    };

    $(function () {
        $('.django-select2').djangoSelect2();
    });

}(this.jQuery));
