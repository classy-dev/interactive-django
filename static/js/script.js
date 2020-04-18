$(function(){
	'use strict';
	
	$('html').removeClass('no-js').addClass('js');

	
	/*=========================================================================
		Menu Functioning
	=========================================================================*/
	$('.menu-btn').on('click', function(e){
		e.preventDefault();
		$('body').toggleClass('show-menu');
	});
	
	$('.menu > ul > li > a').on('click', function(){
		var $offset = $( $(this).attr('href') ).offset().top;
		$('body, html').animate({
			scrollTop: $offset
		}, 700);
		$('body').removeClass('show-menu');
	});
	
	
});