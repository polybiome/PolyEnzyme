$(".navbar-nav a").mouseover(function(){
	$('.navbar-nav>.active>a').css({
		'box-shadow' : 'none'
	});
});
$(".navbar-nav a").mouseout(function(){
	$('.navbar-nav>.active>a').css({
		'box-shadow' : 'inset 0 3px 9px rgba(0,0,0,0.5)'
	});
});
$(window).scroll(function(){
	var topScroll = $(this).scrollTop();
	if (topScroll >=  $(window).height() - 0.5*$('#ribbon').height()){
		$('#ribbon').css({
			'transform' : 'translate(0px, '+ 0 +'px)'
		});
	};
	if(topScroll > $('.food').offset().top - ($(window).height() / 1.2)) {

	$('.food').each(function(i){
	  setTimeout(function(){
	    $('.food').eq(i).addClass('is-showing');
	  }, (700 * (Math.exp(i * 0.14))) - 700);
	});

	}
})