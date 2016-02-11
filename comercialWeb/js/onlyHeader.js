$(document).ready(function(){
$('.navbar').css({
	  'transform' : 'translate(0px, '+ 0 +'px)'
	});
	$(window).scroll(function(){
		var disTop = $(this).scrollTop();
		if (disTop >= 200){
			$(".navbar-fixed-top").addClass('navbarEffect');
		} else{
			$(".navbar-fixed-top").removeClass('navbarEffect');
		};
	});
});