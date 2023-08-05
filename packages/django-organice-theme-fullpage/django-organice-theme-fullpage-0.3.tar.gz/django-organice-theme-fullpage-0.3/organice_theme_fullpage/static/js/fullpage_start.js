/**
 * Pre-process content, and start fullPage
 */

$(document).ready(function () {
	// use first image in each section as section background
	$('#fullpage .section').each(function () {
		var image = $(this).find('img').first();
		var src = image.attr('src');
		if (typeof src !== 'undefined') {
			$(this).css('background-image', 'url(' + src + ')');
			$(this).css('background-position', '50% 50%');
			$(image).remove();
		}
	});
});

function fullPageStart() {
	$('#fullpage').fullpage({
		//anchors: ['1', '2', '3'],
		navigation: true,
		navigationPosition: 'right',
		//navigationTooltips: ['- 1 -', '- 2 -', '- 3 -'],
		resize: false
	});
}
