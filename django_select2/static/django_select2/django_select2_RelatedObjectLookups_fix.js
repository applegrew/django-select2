/*global SelectBox, interpolate*/
// Fixes Django related-objects functionality to allow for the presence of Select2 elements

(function ($) {
    'use strict';

    function dismissChangeRelatedObjectPopup_fixed(win, objId, newRepr, newId) {
        var id = windowname_to_id(win.name).replace(/^edit_/, '');
        var selectsSelector = interpolate('#%s, #%s_from, #%s_to', [id, id, id]);
        var selects = $(selectsSelector);
        // update all django_select2 fields related to the changed object
        var related_model = selects.data("related-model");
        selects = selects.add('*[data-related-model="' + related_model +'"]');
        selects.find('option').each(function () {
            if (this.value === objId) {
                this.textContent = newRepr;
                this.value = newId;
            }
        });
        selects.filter('.django-select2').djangoSelect2();
        win.close();
    }

    function dismissDeleteRelatedObjectPopup(win, objId) {
        var id = windowname_to_id(win.name).replace(/^delete_/, '');
        var selectsSelector = interpolate('#%s, #%s_from, #%s_to', [id, id, id]);
        var selects = $(selectsSelector);
        // update all django_select2 fields related to the deleted object
        var related_model = selects.data("related-model");
        selects = selects.add('*[data-related-model="' + related_model +'"]');

        selects.find('option').each(function() {
            if (this.value === objId) {
                $(this).remove();
            }
        }).trigger('change');
        win.close();
    }

    window.dismissChangeRelatedObjectPopup = dismissChangeRelatedObjectPopup_fixed;
    window.dismissDeleteRelatedObjectPopup = dismissDeleteRelatedObjectPopup;

    $(document).ready(function () {
        $('body').on('change', '.related-widget-wrapper select', function (e) {
            var event = $.Event('django:update-related');
            $(this).trigger(event);
            if (!event.isDefaultPrevented()) {
                updateRelatedObjectLinks(this);
            }
        });
        $('.related-widget-wrapper select').trigger('change');
    });

})(this.jQuery);