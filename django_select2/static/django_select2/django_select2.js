(function ($) {
  var init = function ($element, options) {
    $element.select2(options)
  }

  var initHeavy = function ($element, options) {
    var settings = $.extend({
      ajax: {
        data: function (params) {
          var result = {
            term: params.term,
            page: params.page,
            field_id: $element.data('field_id')
          }
          var namePrefix = $element.closest('div.inline-related').attr('id')
          var elementId = $element.attr('id')
          if (namePrefix && elementId && elementId.indexOf(namePrefix) !== -1) {
            // in case the prefix if failed to fetch correctly reset it
            namePrefix += '-'
          } else {
            namePrefix = ''
          }
          var dependentFields = $element.data('select2-dependent-fields')
          if (dependentFields) {
            dependentFields = dependentFields.trim().split(/\s+/)
            $.each(dependentFields, function (i, dependentField) {
              result[dependentField] = $('[name=' + namePrefix + dependentField + ']', $element.closest('form')).val()
            })
          }

          return result
        },
        processResults: function (data, page) {
          return {
            results: data.results,
            pagination: {
              more: data.more
            }
          }
        }
      }
    }, options)

    $element.select2(settings)
  }

  $.fn.djangoSelect2 = function (options) {
    var settings = $.extend({}, options)
    $.each(this, function (i, element) {
      var $element = $(element)
      if ($element.hasClass('django-select2-heavy')) {
        initHeavy($element, settings)
      } else {
        init($element, settings)
      }
    })
    return this
  }

  $(function () {
    $('.django-select2').djangoSelect2()
  })
}(this.jQuery))
