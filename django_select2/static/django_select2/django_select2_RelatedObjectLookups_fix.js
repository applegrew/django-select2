/*global SelectBox, interpolate*/
// Fixes Django related-objects functionality to allow for the presence of 
// Select2 elements initialised by a later script

(function($) {
    'use strict';

    function dismissAddRelatedObjectPopup(win, newId, newRepr) {
        var name = windowname_to_id(win.name);
        var elem = document.getElementById(name);
        if (elem) {
            var elemName = elem.nodeName.toUpperCase();
            if (elemName === 'SELECT') {
                elem.options[elem.options.length] = new Option(newRepr, newId, true, true);
            } else if (elemName === 'INPUT') {
                if (elem.className.indexOf('vManyToManyRawIdAdminField') !== -1 && elem.value) {
                    elem.value += ',' + newId;
                } else {
                    elem.value = newId;
                }
            }
            // Trigger a change event to update related links if required.
            $(elem).trigger('change');
        } else {
            var toId = name + "_to";
            var o = new Option(newRepr, newId);
            SelectBox.add_to_cache(toId, o);
            SelectBox.redisplay(toId);
        }
        win.close();
    }

    function dismissChangeRelatedObjectPopup_fixed(win, objId, newRepr, newId) {
        var id = windowname_to_id(win.name).replace(/^edit_/, '');
        var selectsSelector = interpolate('#%s, #%s_from, #%s_to', [id, id, id]);
        var selects = $(selectsSelector);
        selects.find('option').each(function() {
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
        selects.find('option').each(function() {
            if (this.value === objId) {
                $(this).remove();
            }
        }).trigger('change');
        win.close();
    }

    window.dismissAddRelatedObjectPopup = dismissAddRelatedObjectPopup;
    window.dismissChangeRelatedObjectPopup = dismissChangeRelatedObjectPopup_fixed;
    window.dismissDeleteRelatedObjectPopup = dismissDeleteRelatedObjectPopup;

    $(document).ready(function() {
        $('body').on('change', '.related-widget-wrapper select', function(e) {
            var event = $.Event('django:update-related');
            $(this).trigger(event);
            if (!event.isDefaultPrevented()) {
                updateRelatedObjectLinks(this);
            }
        });
        $('.related-widget-wrapper select').trigger('change');
    });

})(this.jQuery);