if (!window['django_select2']) {
	// This JS file can be included multiple times. So, as not to overwrite previous states, we run this only once.

	window.django_select2 = {
		MULTISEPARATOR: String.fromCharCode(31), // We use this unprintable char as separator,
												// since this can't be entered by user.
		get_url_params: function (term, page, context) {
			var field_id = jQuery(this).data('field_id'),
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
				jQuery(this).data('results', results.results);
			} else {
				jQuery(this).removeData('results');
			}
			return results;
		},
		onValChange: function () {
			django_select2.updateText(jQuery(this));
		},
		prepareValText: function (vals, txts, isMultiple) {
			var data = []
			jQuery(vals).each(function (index) {
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
		updateText: function ($e) {
			var val = $e.select2('val'), data = $e.select2('data'), txt = $e.txt(), isMultiple = !!$e.attr('multiple'),
				diff;

			if (val || val === 0) { // Means value is set. A numerical 0 is also a valid value.
				if (isMultiple) {
					if (val.length !== txt.length) {
						txt = [];
						jQuery(val).each(function (idx) {
							var i, value = this, id;

							for (i in data) {
								id = data [i].id;
								if (id instanceof String) {
									id = id.valueOf();
								}
								if (id == value) {
									txt.push(data[i].text);
								}
							}
						});
					}
				} else {
					txt = data.text;
				}
				$e.txt(txt);
			} else {
				$e.txt('');
			}
		},
		getValText: function ($e) {
			var val = $e.select2('val'), res = $e.data('results'), txt = $e.txt(), isMultiple = !!$e.attr('multiple'),
				f, id = $e.attr('id');
			if (val || val === 0) { // Means value is set. A numerical 0 is also a valid value.

				if (!isMultiple) {
					val = [val];
					if (txt || txt === 0) {
						txt = [txt];
					}
				}

				if (txt === 0 || (txt && val.length === txt.length)) {
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
					jQuery(val).each(function (idx) {
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
			}
			return null;
		},
		onInit: function (e, callback) {
			e = jQuery(e);
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
			django_select2.updateText(e);
		},
		createSearchChoice: function(term, data) {
			if (!data || jQuery(data).filter(function () {
				return this.text.localeCompare(term) === 0;
			}).length === 0) {
				return {
					id: term,
					text: term
				};
			}
		},
		onMultipleHiddenChange: function () {
			var $e = jQuery(this), valContainer = $e.data('valContainer'), name = $e.data('name'), vals = $e.val();
			valContainer.empty();
			if (vals) {
				vals = vals.split(django_select2.MULTISEPARATOR);
				jQuery(vals).each(function () {
					var inp = jQuery('<input type="hidden">').appendTo(valContainer);
					inp.attr('name', name);
					inp.val(this);
				});
			}
		},
		initMultipleHidden: function ($e) {
			var valContainer;

			$e.data('name', $e.attr('name'));
			$e.attr('name', '');

			valContainer = jQuery('<div>').insertAfter($e).css({'display': 'none'});
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
				var args = Array.prototype.slice.call(arguments, 0);
		        return f.apply(jQuery('#' + id).get(0), args);
		    }
		},
		logErr: function () {
			if (console && console.error) {
	            args = Array.prototype.slice.call(arguments);
	            console.error.apply(console, args);
	        }
		}
	};

	(function (isDebug) { // Only used for debugging.
		if (isDebug) {
			for (var i in django_select2) {
				var f = django_select2[i];
				if (typeof(f) == "function") {
					django_select2[i] = (function (i, f) {
						return function () {
							console.log('Function ' + i + ' called for object: ', this);
							return f.apply(this, arguments);
						};
					}(i, f));
				}
			}
		}
	}(false));

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
				} else {
					this.removeAttr('txt');
				}
				return this;
			} else {
				val = this.attr('txt');
				if (this.attr('multiple')) {
					if (val) {
						val = val.split(django_select2.MULTISEPARATOR);
					} else {
						val = [];
					}
				}
				return val;
			}
		};
	})( jQuery );
}
