// Fixes Django admin related objects functionality for select2 elements
(function ($) {
  'use strict'

  function dismissChangeRelatedObjectPopupFixed (win, objId, newRepr, newId) {
    var id = window.windowname_to_id(win.name).replace(/^edit_/, '')
    var selectsSelector = window.interpolate('#%s, #%s_from, #%s_to', [id, id, id])
    var selects = $(selectsSelector)
    // update all django_select2 fields related to the changed object
    var relatedModel = selects.data('related-model')
    selects = selects.add('*[data-related-model="' + relatedModel + '"]')
    selects.find('option').each(function () {
      if (this.value === objId) {
        this.textContent = newRepr
        this.value = newId
      }
    })
    selects.filter('tr:not(.empty-form) .django-select2').djangoSelect2()
    win.close()
  }

  function dismissDeleteRelatedObjectPopupFixed (win, objId) {
    var id = window.windowname_to_id(win.name).replace(/^delete_/, '')
    var selectsSelector = window.interpolate('#%s, #%s_from, #%s_to', [id, id, id])
    var selects = $(selectsSelector)
    // update all django_select2 fields related to the deleted object
    var relatedModel = selects.data('related-model')
    selects = selects.add('*[data-related-model="' + relatedModel + '"]')
    selects.find('option').each(function () {
      if (this.value === objId) {
        $(this).remove()
      }
    }).trigger('change')
    win.close()
  }

  window.dismissChangeRelatedObjectPopup = dismissChangeRelatedObjectPopupFixed
  window.dismissDeleteRelatedObjectPopup = dismissDeleteRelatedObjectPopupFixed

  $(document).ready(function () {
    $('body').on('change', '.related-widget-wrapper select', function (e) {
      var event = $.Event('django:update-related')
      $(this).trigger(event)
      if (!event.isDefaultPrevented()) {
        window.updateRelatedObjectLinks(this)
      }
    })

    $('.related-widget-wrapper select').trigger('change')
  })
})(this.jQuery)
