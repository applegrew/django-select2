
var django_select2 = {
	get_url_params: function (term, page, context) {
		return {
			'term': term,
			'page': page,
			'context': context
		};
	},
	process_results: function (data, page, context) {
		var results;
		if (data.err && data.err.toLowerCase() === 'nil') {
			results = {
				'results': data.results
			};
			if (context) {
				results['context'] = context;
			}
			if (data.more === true || data.more === false) {
				results['more'] = data.more;
			}
		} else {
			results = {'results':[]};
		}
		return results;
	}
};