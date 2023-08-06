
$(document).ready(function()
{
	/*
		de-obfuscate obfuscated text, such as email addresses
	*/
	$('.obfuscated').each(function(k) {
		var cypher = $(this).find('span').get(0).innerHTML;
		var clear = deobfuscate(cypher);
		if ($(this).is('.obfuscated_email')) {
			clear = '<a href="mailto:' + clear + '">' + clear + '</a>';
		}
		$(this).replaceWith('<span class="deobfuscated" title="This value has been un-hidden using javascript.">' + clear + '</span>');
	});

	/*
		select text in autofocus fields
	*/
	$('[autofocus]').each(function(k, elem) {
		$(elem).select();
	});

	/*
		Dropdown closes as soon as search field is clicked; prevent that.
	 */
	$('#menu-search-dropdown').click(function(event)
	{
		event.stopPropagation();
	});

	/*
		When selecting a dropdown that has inputs, focus and select the first field.
	 */
	function focus_and_select_input(elem)
	{
		elem.select();
		elem.focus();
	}
	$('.dropdown-toggle').click(function(event)
	{
		var inputs = $(this).parent().find('input');
		if (inputs.length)
		{
			var input = inputs.first();
			setTimeout(focus_and_select_input.bind(null, input), 0);
		}
	});

	/*
		Let ctrl+H open the search bar.
		http://stackoverflow.com/a/14180949/723090
	 */
	$(window).bind('keydown', function(event)
	{
		if (event.ctrlKey || event.metaKey) {
			switch (String.fromCharCode(event.which).toLowerCase())
			{
				case 'h':
					event.preventDefault();
					var msdb = $('#menu-search-dropdown-button');
					if (msdb.is(":visible"))
					{
						/* The search is in dropdown menu mode */
						var input = $('#menu-search-dropdown').find('input').first();
						msdb.click();
					}
					else
					{
						var msm = $('#menu-search-mainbar');
						/* The search is in menubar mode, but it might be collapsed */
						if ( ! msm.is(":visible"))
						{
							/* It's collapsed; probably the user doesn't have a ctrl key if their screen is this small... */
							$('#menubar-toggle-collapse').click();
						}
						var input = msm.find('input').first();
					}
					setTimeout(focus_and_select_input.bind(null, input), 0);
					break;
			}
		}
	});

	/*
		Add square_image_portrait to square_image_*, see CSS for notes.

		The square_image_* wrappers should contain a single image.
	 */
	$('.square_image_64, .square_image_128, .square_image_256').each(function (k, wrapper) {
		var wrapper = $(wrapper);
		var imgs = wrapper.find('img');
		if (imgs.length == 1)
		{
			var img = $(imgs[0]);
			img.ready(function (img, wrapper) {
				if (img.naturalWidth < img.naturalHeight)
				{
					wrapper.addClass('square_image_portrait');
				}
			}.bind(null, img[0], wrapper))
		}
	});

	/*
		Autocompletion for search using a continuation of typehead.

		Relies on autocomplete_url being set and that url returning json matches.

		https://github.com/bassjobsen/Bootstrap-3-Typeahead
	 */
	var $input = $('.search-typeahead');
	$input.typeahead({
		minLength: 2,
		items: 7,
		delay: 100,
		autoSelect: true,
		source: function (query, process)
		{
			$.getJSON(autocomplete_url + '?q=' + query, function(process, data)
			{
				process(data);

			}.bind(null, process));
		},
		afterSelect: function (element)
		{
			console.log('selected', element);
			if (element.url)
			{
				console.log('redirect', element.url);
				window.location.href = element.url;
			}
		},
	});
});

/*
	'Fix' modulo (use the mathematical definition for negative numbers)
	http://stackoverflow.com/questions/4467539/javascript-modulo-not-behaving
*/
function mod(a, n)
{
	return a - (n * Math.floor(a/n));
}

/*
	Make text readable that has been hidden to prevent crawling.
 */
function deobfuscate_letter(letter, pos)
{
	var encchars = document.settings.ENCCHARS;
	var nr = encchars.indexOf(letter);
	if (nr < 0) { return letter; }
	var oldnr = mod(nr - pos*pos - 42, encchars.length);
	return encchars.charAt(oldnr);
}

function deobfuscate(text)
{
	var clear = '';
	for (var i = 0; i < text.length; i += 1)
	{
		clear += deobfuscate_letter(text[i], i)
	}
	return clear
}


