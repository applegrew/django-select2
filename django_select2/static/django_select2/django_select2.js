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

          var dependentFields = $element.data('select2-dependent-fields')
          if (dependentFields) {
            dependentFields = dependentFields.trim().split(/\s+/)
            $.each(dependentFields, function (i, dependentField) {
              result[dependentField] = $('[name=' + dependentField + ']', $element.closest('form')).val()
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
        var $selectedOption = $element.find(':selected')
        if ($selectedOption.val() & !$selectedOption.text()) {
          $.ajax({
            type: $element.data('ajax--type'),
            url: $element.data('ajax--url') + $selectedOption.val(),
            dataType: 'json'
          }).then(function (data) {
            $selectedOption.text(data.text)
            $selectedOption.removeData()
            $element.trigger('change')
          })
        }
      } else {
        init($element, settings)
      }
    })
    return this
  }

  $(function () {
    // do not trigger select2 initialization in hidden admin inline formset rows
    $('.django-select2').not('.empty-form .django-select2').djangoSelect2()
  })
}(this.jQuery))
