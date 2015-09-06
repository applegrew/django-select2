$(function () {
    $('.django-select2').each(function () {
        var field_id = $(this).data('field_id');
        $(this).select2({
            ajax: {
                data: function (params) {
                    return {
                        term: params.term,
                        page: params.page,
                        field_id: field_id
                    };
                },
                processResults: function (data, page) {
                  return {
                    results: data.results
                  };
                }
            }
        });
    });
});

