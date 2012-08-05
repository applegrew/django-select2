
var django_select2 = {
	get_url_params: function (term, page, context) {
		var field_id = $(this).data('field_id'),
			res = {
				'term': term,
				'page': page,
				'context': context
			};
		if (field_id) {
			res['field_id'] = field_id;
		}
		return res;
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
		if (results.results) {
			$(this).data('results', results.results);
		} else {
			$(this).removeData('results');
		}
		return results;
	},
	setCookie: function (c_name, value) {
		document.cookie=c_name + "=" + escape(value);
	},
	getCookie: function (c_name) {
		var i,x,y,ARRcookies=document.cookie.split(";");
		for (i=0; i<ARRcookies.length; i++) {
			x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
			y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
			x=x.replace(/^\s+|\s+$/g,"");
			if (x==c_name) {
				return unescape(y);
			}
		}
	},
	delCookie: function (c_name) {
		document.cookie = c_name + '=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
	},
	onValChange: function () {
		var e = $(this), res = e.data('results'), val = e.val(), txt, id = e.attr('id');
		
		if (res) {
			for (var i in res) {
				if (res[i].id == val) {
					val = res[i].id; // To set it to correct data type.
					txt = res[i].text;
					break;
				}
			}
			if (txt) {
				// Cookies are used to persist selection's text. This needed
				//when the form springs back if there is any validation failure.
				django_select2.setCookie(id + '_heavy_val', val);
				django_select2.setCookie(id + '_heavy_txt', txt);
				return;
			}
		}
		django_select2.delCookie(id + '_heavy_val');
		django_select2.delCookie(id + '_heavy_txt');
	},
	onInit: function (e) {
		e = $(e);
		var id = e.attr('id'),
			val = django_select2.getCookie(id + '_heavy_val'),
			txt = django_select2.getCookie(id + '_heavy_txt');

		if (txt && e.val() == val) {
			// Restores persisted value text.
			return {'id': val, 'text': txt};
		} else {
			e.val(null);
		}
		return null;
	}
};