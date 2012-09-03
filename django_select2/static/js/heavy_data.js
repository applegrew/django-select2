if (!window['django_select2']) {
	// This JS file can be included multiple times. So, as not to overwrite previous states, we run this only once.

	var django_select2 = {
		MULTISEPARATOR: String.fromCharCode(0), // We use this unprintable char as separator,
												// since this can't be entered by user.
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
			document.cookie = c_name + "=" + escape(value);
		},
		getCookie: function (c_name) {
			var i, x, y, ARRcookies = document.cookie.split(";");

			for (i = 0; i < ARRcookies.length; i++) {
				x = ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
				y = ARRcookies[i].substr(ARRcookies[i].indexOf("=") + 1);
				x = x.replace(/^\s+|\s+$/g,"");
				if (x == c_name) {
					return unescape(y);
				}
			}
		},
		delCookie: function (c_name, isStartsWithPattern) {
			var i, x, ARRcookies;

			if (!isStartsWithPattern) {
				document.cookie = c_name + '=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
			} else {
				ARRcookies = document.cookie.split(";");

				for (i = 0; i < ARRcookies.length; i++) {
					x = ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
					x = x.replace(/^\s+|\s+$/g,"");
					if (x.indexOf(c_name) == 0) {
						document.cookie = c_name + '=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
					}
				}
			}
		},
		onValChange: function () {
			var e = $(this), res, id = e.attr('id');

			res = django_select2.getValText(e, false);
			
			if (res && res[1]) {
				// Cookies are used to persist selection's text. This is needed
				// when the form springs back if there is any validation failure.
				$(res[0]).each(function (idx) {
					var txt = res[1][idx];
					if (typeof(txt) !== 'undefined') {
						django_select2.setCookie(id + '_heavy_val:' + idx, this);
						django_select2.setCookie(id + '_heavy_txt:' + idx, txt);
					}
				});
			} else {
				django_select2.delCookie(id + '_heavy_val:', true);
				django_select2.delCookie(id + '_heavy_txt:', true);
			}
		},
		prepareValText: function (vals, txts, isMultiple) {
			var data = []
			$(vals).each(function (index) {
				data.push({id: this, text: txts[index]});
			});
			if (isMultiple) {
				return data;
			} else {
				if (data.length > 0) {
					return data[0];
				} else {
					return null;
				}
			}
		},
		getValText: function ($e, isGetFromCookieAllowed) {
			var val = $e.select2('val'), res = $e.data('results'), txt = $e.txt(), isMultiple = !!$e.attr('multiple'),
				f, id = $e.attr('id');
			if (val || val === 0) { // Means value is set. A numerical 0 is also a valid value.

				if (!isMultiple) {
					val = [val];
					if (txt || txt === 0) {
						txt = [txt];
					}
				}

				if (txt || txt === 0) {
					return [val, txt];
				}

				f = $e.data('userGetValText');
				if (f) {
					txt = f($e, val, isMultiple);
					if (txt || txt === 0) {
						return [val, txt];
					}
				}
				
				if (res) {
					txt = [];
					$(val).each(function (idx) {
						var i, value = this;
						
						for (i in res) {
							if (res[i].id == value) {
								val[idx] = res[i].id; // To set it to correct data type.
								txt.push(res[i].text);
							}
						}
					});
					if (txt || txt === 0) {
						return [val, txt];
					}
				}

				if (isGetFromCookieAllowed) {
					txt = [];
					$(val).each(function (idx) {
						var value = this, cookieVal;

						cookieVal = django_select2.getCookie(id + '_heavy_val:' + idx);
						
						if (cookieVal == value) {
							txt.push(django_select2.getCookie(id + '_heavy_txt:' + idx));
						}
					});
					if (txt || txt === 0) {
						return [val, txt];
					}
				}

			}
			return null;
		},
		onInit: function (e, callback) {
			e = $(e);
			var id = e.attr('id'), data = null, val = e.select2('val');

			if (!val && val !== 0) {
				val = e.data('initVal');
			}

			if (val || val === 0) {
				// Value is set so need to get the text.
				data = django_select2.getValText(e);
				if (data && data[0]) {
					data = django_select2.prepareValText(data[0], data[1], !!e.attr('multiple'));
				}
			}
			if (!data) {
				e.val(null); // Nulling out set value so as not to confuse users.
			}
			callback(data); // Change for 2.3.x
		},
		onMultipleHiddenChange: function () {
			var $e = $(this), valContainer = $e.data('valContainer'), name = $e.data('name'), vals = $e.val();
			valContainer.empty();
			if (vals) {
				vals = vals.split(django_select2.MULTISEPARATOR);
				$(vals).each(function () {
					var inp = $('<input type="hidden">').appendTo(valContainer);
					inp.attr('name', name);
					inp.val(this);
				});
			}
		},
		initMultipleHidden: function ($e) {
			var valContainer;

			$e.data('name', $e.attr('name'));
			$e.attr('name', '');

			valContainer = $('<div>').insertAfter($e).css({'display': 'none'});
			$e.data('valContainer', valContainer);

			$e.change(django_select2.onMultipleHiddenChange);
			if ($e.val()) {
				$e.change();
			}
		},
		convertArrToStr: function (arr) {
			return arr.join(django_select2.MULTISEPARATOR);
		},
		runInContextHelper: function (f, id) {
			return function () {
				var args = Array.prototype.slice.call(arguments);
		        return f.apply($('#' + id).get(0), args);
		    }
		}
	};

	(function( $ ){
		// This sets or gets the text lables for an element. It merely takes care returing array or single
		// value, based on if element is multiple type.
		$.fn.txt = function(val) {
			if (typeof(val) !== 'undefined') {
				if (val) {
					if (val instanceof Array) {
						if (this.attr('multiple')) {
							val = django_select2.convertArrToStr(val);
						} else {
							val = val[0]
						}
					}
					this.attr('txt', val);
				}
				return this;
			} else {
				val = this.attr('txt');
				if (val && this.attr('multiple')) {
					val = val.split(django_select2.MULTISEPARATOR);
				}
				return val;
			}
		};
	})( jQuery );
}